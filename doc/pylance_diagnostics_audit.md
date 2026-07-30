# Pyright/Pylance Diagnostics Audit & Remediation Plan

Audience: anyone touching type-checked code in this repo. Pylance (the VS Code extension) is a wrapper around Microsoft's `pyright` type checker — this audit runs `pyright` directly against the whole codebase so the findings are exhaustive and reproducible, not limited to whatever files happen to be open in an editor at a given moment.

## Methodology

- Tool: `npx pyright` v1.1.411 (no `pyrightconfig.json`/`[tool.pyright]` exists in this repo, and `.vscode/settings.json` sets no `python.analysis.typeCheckingMode`, so both the CLI and the user's actual Pylance run in the same unconfigured **basic** mode — this audit's findings match what Pylance already shows in the editor).
- Scope: `src/` and `scripts/` (the actual application code and operational tooling), pointed explicitly at the project's `myenv` virtualenv via `--pythonpath` so third-party stubs (SQLAlchemy, Pydantic, Docling, Qdrant, …) resolve correctly. `tests/` was excluded from this pass — test doubles/fakes are *expected* to duck-type loosely against real classes, which is a different, much noisier category not worth mixing into a "fix the app code" audit; happy to re-run scoped to `tests/` separately if wanted.
- Result: **1,871 files analyzed, 429 errors + 34 warnings = 463 diagnostics across 116 files.**
- Deprecation warnings were checked two ways, both clean: pyright's static `reportDeprecated` rule found **zero** hits (it's off by default in basic mode, matching this repo's config either way), and a full `pytest tests/unit` run with default warning filters surfaced **zero** `DeprecationWarning`/`PendingDeprecationWarning`s in the "warnings summary" section. Nothing to fix here today — re-check after any major dependency bump (SQLAlchemy, Pydantic, Docling all deprecate aggressively across major versions).

## Progress

- **Phase A — done.** All 9 `__getattr__` files got `TYPE_CHECKING`-guarded static imports (see Priority 1 below). Verified: pyright went from 429 errors/34 warnings to **370 errors/0 warnings** (93 diagnostics eliminated — all 34 `reportUnsupportedDunderAll` warnings plus 59 downstream `reportCallIssue`/`reportAttributeAccessIssue`/`reportArgumentType` errors). Full `pytest tests/unit tests/integration` run afterward: same pass count, same single pre-existing unrelated failure — zero behavior regressions, as expected for a change that's stripped entirely at runtime.

## How to read this document

The 463 raw diagnostics are **not** 463 independent problems. Investigation shows a small number of systemic root causes account for the large majority of them. This document is organized by root cause (most impactful first), not by raw pyright rule name, because that's what makes the fix effort tractable: fixing one pattern in one place can resolve dozens of listed diagnostics at once. Each section states what's confirmed by reading the actual source (not just inferred from the message shape) versus what's strongly suspected by the same symptom signature recurring in files that share the same known cause.

---

## Priority 1 — Lazy `__getattr__` package re-exports break static type inference (~130–190 of 429 diagnostics — the single largest cause)

### The pattern

Nine `__init__.py` files in this codebase use a deliberate lazy-import convention: instead of eager `from .module import Name` statements, they implement [PEP 562](https://peps.python.org/pep-0562/) module-level `__getattr__`, resolving each exported name to its real module only when actually accessed:

```python
# src/application/workflows/parsing/tables/structure/__init__.py
__all__ = [
    "TableHeaderPathBuilder",
    "TableShapeResolver",
    "TableStructureContextRenderer",
    "TableStructureSummary",
    "TableStructureSummaryBuilder",
]

def __getattr__(name: str):
    if name == "TableHeaderPathBuilder":
        from .table_header_path_builder import TableHeaderPathBuilder
        return TableHeaderPathBuilder
    if name == "TableShapeResolver":
        from .table_shape_resolver import TableShapeResolver
        return TableShapeResolver
    ...
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

This is a real, intentional convention in this repo (referenced elsewhere as avoiding "package `__init__.py` facades" and heavy eager imports at module load time). It works perfectly at runtime. **Pyright cannot follow it.** A static analyzer has no way to know, for a given `__getattr__`, which `if name == ...` branch will fire for a specific imported symbol — so it infers the function's return type as the **union of every `return X` statement inside it**. Every name imported from one of these modules is therefore typed as `type[TableHeaderPathBuilder] | type[TableShapeResolver] | type[TableStructureContextRenderer] | type[TableStructureSummary] | type[TableStructureSummaryBuilder]` — regardless of which one was actually asked for — and pyright then validates every call/attribute-access against **all five**, reporting an error for every union member that doesn't match.

### The 9 affected files

```
src/application/services/answer_generation/__init__.py
src/application/workflows/parsing/__init__.py
src/application/workflows/parsing/tables/__init__.py
src/application/workflows/parsing/tables/normalization/__init__.py
src/application/workflows/parsing/tables/rendering/__init__.py
src/application/workflows/parsing/tables/structure/__init__.py
src/application/workflows/question_answering/__init__.py
src/application/workflows/question_answering/answer_context/__init__.py
src/infrastructure/retrieval/keyword/__init__.py
```

95 files import from these 9 modules (some from more than one); confirmed diagnostics land in at least 20 of them.

### Confirmed examples (read the actual source, not just pattern-matched)

**`reportUnsupportedDunderAll` — 34/34 diagnostics, 100% this cause.** Every one of the 9 files' `__all__` list gets flagged ("X is specified in `__all__` but is not present in module") because pyright only sees the plain module namespace, not what `__getattr__` would dynamically provide.

**`src/application/workflows/parsing/builders/document_graph_builder.py:104-105`** — this is the *exact* example quoted in the original ask:
```python
self.logical_table_family_resolver = LogicalTableFamilyResolver()   # zero-arg call
self.table_semantic_resolver = TableSemanticResolver()                # zero-arg call
```
Pyright reports **"Arguments missing for parameters `logical_table_family_id`, `family_index`, `family_total`, `continuation_role`"** on both lines. Neither `LogicalTableFamilyResolver` nor `TableSemanticResolver` takes those parameters — `LogicalTableFamilyAssignment` does (a dataclass with exactly those 4 required fields), and it's a **different name from the same lazy `__getattr__`** in `src/application/workflows/parsing/tables/__init__.py`. Pyright checked the zero-arg call against the wrong union member.

**`src/application/orchestrator/ingestion/parsing_runtime_builder.py:51-63`** — constructing `ParsingWorkflow(parser=..., normalizer=..., ...)` (all correct kwargs for `ParsingWorkflow.__init__`) reports "No parameter named 'parser'", "No parameter named 'normalizer'", etc., because `ParsingWorkflow` is imported from `src/application/workflows/parsing/__init__.py`'s lazy `__getattr__` alongside `ParsingWorkflowResult`, and pyright checked the call against `ParsingWorkflowResult`'s (unrelated) dataclass signature too.

**`src/application/agent_runtime/bootstrap/agent_service_builder.py:106-109`** — `AnswerGenerationService(llm_service=..., answer_generation_model=...)` reports "No parameter named 'llm_service'" / "No parameter named 'answer_generation_model'", because `AnswerGenerationService` is imported from `src/application/services/answer_generation/__init__.py` alongside `AnswerIntent`, `AnswerFormatPolicy`, etc., none of which have those constructor params.

**`src/application/workflows/parsing/tables/table_semantic_resolver.py:25`** — `TableStructureSummaryBuilder()` (zero-arg) reports "Arguments missing for parameters `table_shape`, `quality_score`" — those belong to `TableStructureSummary`, a sibling union member from the same `tables/structure/__init__.py`.

### Full list of confirmed/strongly-suspected consumer files (diagnostic count in that file attributable to this cause)

```
11  src/application/workflows/question_answering/evidence/table_evidence_hydrator.py
 9  src/application/orchestrator/ingestion/parsing_runtime_builder.py
 8  src/application/workflows/parsing/tables/semantics/table_semantic_classifier.py
 7  scripts/ask_document.py
 7  src/application/agent_runtime/bootstrap/agent_service_builder.py
 6  src/application/workflows/extraction/batching/extraction_table_chunk_hydrator.py
 6  src/application/workflows/parsing/builders/document_graph_builder.py
 5  src/application/workflows/parsing/tables/table_semantic_resolver.py
 1  src/application/orchestrator/retrieval/retrieval_runtime_builder.py
```
Plus all 34 `reportUnsupportedDunderAll` hits (9 files) and a further ~50-70 diagnostics scattered as single-line "No parameter named X" / "Cannot access attribute Y for class Z1/Z2/Z3" entries inside `src/application/workflows/parsing/tables/*` and `src/application/workflows/question_answering/*` consumers not individually re-verified line-by-line here (same symptom signature, same 9-file cause).

### The fix

Add a `TYPE_CHECKING`-guarded block of **plain, static** imports alongside the existing `__getattr__` in each of the 9 files. `TYPE_CHECKING` is `False` at runtime, so this costs **zero** runtime overhead and changes **zero** runtime behavior — it exists purely so pyright's static pass sees real, per-name types instead of inferring a union from the dynamic function body:

```python
from typing import TYPE_CHECKING

__all__ = [
    "TableHeaderPathBuilder",
    "TableShapeResolver",
    "TableStructureContextRenderer",
    "TableStructureSummary",
    "TableStructureSummaryBuilder",
]

if TYPE_CHECKING:
    from src.application.workflows.parsing.tables.structure.table_header_path_builder import (
        TableHeaderPathBuilder,
    )
    from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
        TableShapeResolver,
    )
    from src.application.workflows.parsing.tables.structure.table_structure_context_renderer import (
        TableStructureContextRenderer,
    )
    from src.application.workflows.parsing.tables.structure.table_structure_summary import (
        TableStructureSummary,
    )
    from src.application.workflows.parsing.tables.structure.table_structure_summary_builder import (
        TableStructureSummaryBuilder,
    )


def __getattr__(name: str):
    # unchanged — still lazy at runtime
    ...
```

This is the standard, well-known idiom for typed lazy-import modules (used by CPython's own stdlib stubs for the same reason). Apply it to all 9 files verbatim — each just needs its own `if TYPE_CHECKING:` block mirroring its existing `__getattr__` branches.

**Risk: effectively none.** No runtime code path changes. **Payoff: eliminates all 34 `reportUnsupportedDunderAll` warnings plus an estimated 100-150+ downstream `reportCallIssue`/`reportAttributeAccessIssue`/`reportArgumentType` diagnostics** across every consumer of these 9 modules, present and future.

---

## Priority 2 — `Optional` narrowing doesn't survive across closures or separate methods (~10-15 diagnostics, concentrated in the core parsing path)

### The pattern

This is the second literal example from the original ask (`"enrich" is not a known attribute of "None"`). A constructor stores an `Optional`-typed collaborator (`self.x: SomeType | None = None`), a guard checks `if self.x is not None: ...`, but the actual `self.x.method(...)` call happens **inside a lambda** or **inside a different method** than the one holding the guard. Pyright's type narrowing is scoped to the block where the check occurs and does not follow `self.attribute` references into a closure or a separate call frame, because it can't prove the attribute won't change in between (even when, as here, it never actually does).

### Confirmed instances

**`src/application/workflows/parsing/parsing_workflow.py`** — three separate instances in one file:
- **L140**: `operation=lambda: self.canonical_element_ocr_enricher.enrich(...)`, guarded by `if self.canonical_element_ocr_enricher is not None and ...:` a few lines above (L128-131) — but the guard's narrowing doesn't extend into the lambda body.
- **L164**: same shape — `operation=lambda: self.page_ocr_fallback_workflow.run(...)`, guarded at L152-154.
- **L249**: `self.document_graph_validator.validate(...)` inside `_validate_document_graph()`, a **separate method** only ever called from one guarded call site (`if self.document_graph_validator is not None: run_stage(..., operation=lambda: self._validate_document_graph(document_graph), ...)` at L210-216) — pyright has no visibility at all into the caller's guard from inside the callee method.

**`src/application/workflows/parsing/runtime/parsing_stage_heartbeat.py:48`** — `self.progress_callback(...)` inside `_run()`, which executes on a **background `Thread`** (`self._thread = Thread(target=self._run, ...)`), while the `None` guard lives in `start()`. Same root limitation, arguably *more* legitimate here since it's genuinely cross-thread, even though in practice `start()` never spawns the thread when the callback is `None`.

Also flagged with the same shape (not individually re-verified): `src/application/workflows/parsing/ocr/page_ocr_fallback_workflow.py`, `src/application/langgraph/nodes/control/route_request_node.py`, `src/application/workflows/parsing/ocr/selection/ocr_target_selector.py`.

### The fix

Two idiomatic options, pick per call site:

**A. Capture the narrowed value into a local before closing over it** (for the lambda cases):
```python
if (
    self.canonical_element_ocr_enricher is not None
    and resolved_ocr_policy.canonical_enrichment_enabled
):
    enricher = self.canonical_element_ocr_enricher  # local: pyright narrows and the lambda closes over this, not self.x
    canonical_elements = run_stage(
        ...
        operation=lambda: enricher.enrich(canonical_elements, activity_context=activity_context),
        ...
    )
```

**B. Assert the invariant at the top of the separate method** (for the `_validate_document_graph`/`_run` cases — also self-documents the precondition):
```python
def _validate_document_graph(self, document_graph: DocumentGraph) -> None:
    assert self.document_graph_validator is not None
    validation = self.document_graph_validator.validate(document_graph)
    validation.raise_if_invalid()
```

**Risk: none** — purely additive narrowing hints; no behavior change.

---

## Priority 3 — Loosely-typed metadata dicts flow into `int()`/`float()` calls and strongly-typed dataclass constructors (~110-140 diagnostics)

This is one underlying issue with two distinct manifestations, both stemming from the same design: Docling's parsed output and derived table/chunk metadata are carried around as `dict[str, object]` "parser extra" bags (deliberately loose, since the underlying data is heterogeneous third-party output), then read back out with `.get(...)` and fed directly into narrowly-typed call sites without an explicit coercion step in between.

### 3a — Raw `int(...)`/`float(...)` on `object`-typed values (~55 diagnostics)

Pattern: `int(data.get("row_start", 0))` where `data: dict[str, object]`. `.get()` returns `object`, and `object` doesn't structurally satisfy `int()`'s `SupportsInt`/`ConvertibleToInt` parameter type, so pyright flags every such call.

Heaviest files:
```
17  src/domain/assets/table_parallel_stream.py
11  scripts/profile_graph_build.py
10  src/domain/assets/table_cell_span.py
 5  src/application/workflows/parsing/builders/document_graph/parsed_asset_factory.py
 3  scripts/run_answer_quality_judge.py
 3  src/application/workflows/retrieval/deduplication/retrieved_chunk_deduplicator.py
 3  src/infrastructure/db/repositories/document/document_graph_value_cleaners.py
```

The codebase already has `src/application/workflows/parsing/parsing_value_coercion.py` with `coerce_positive_int(value: Any) -> int | None` and `coerce_float(value: Any) -> float | None`. **These are not a drop-in fix for every site** — `coerce_positive_int` rejects `0` (returns `None`), which is wrong for fields like `row_start`/`col_start` where `0` is a legitimate, common value (the first row/column). Recommend adding a sibling `coerce_int(value: object, *, default: int = 0) -> int` (no positivity constraint, always returns a plain `int`) for the `from_dict`-style deserialization methods in `table_cell_span.py`/`table_parallel_stream.py`, and auditing the other sites case by case for which existing helper (or a `cast(...)` after a runtime check) actually fits.

### 3b — `object`/`object | None` passed directly into dataclass constructors (~40-50 diagnostics)

Pattern, and the exact literal example from the original ask:
```python
# src/application/workflows/parsing/builders/chunking/builders/fragment/chunk_fragment_builder.py:238-244
fragment.logical_table_family_id = table_metadata.get("logical_table_family_id")           # object | None -> str | None
fragment.logical_table_family_index = table_metadata.get("logical_table_family_index")     # object | None -> int | None
fragment.logical_table_family_total = table_metadata.get("logical_table_family_total")     # object | None -> int | None
fragment.logical_table_continuation_role = table_metadata.get("logical_table_continuation_role")  # object | None -> str | None
```
`table_metadata` is a `dict[str, object]` bag built elsewhere; each `.get()` call is assigned straight into a `ChunkFragment` field typed `str | None`/`int | None` with no cast in between.

Also present in: `src/application/workflows/parsing/builders/chunking/builders/fragment/logical_table_family_fragment_builder.py` (4), `src/application/workflows/parsing/tables/families/logical_table_family_asset_composer.py` (3).

**Fix, in order of preference:**
1. **Best, larger effort:** give `table_metadata` a real shape — a `TypedDict` or small dataclass built once at the point it's produced, instead of a bare `dict[str, object]` passed downstream. This eliminates the whole category at its source rather than patching every consumption site.
2. **Smaller, immediate:** cast at each consumption site with the same defensive style already used elsewhere in this file (e.g. `str(value) if (value := table_metadata.get("logical_table_family_id")) is not None else None`).

Recommend (1) as a follow-up if the team wants this class of finding to stay fixed as new fields are added; (2) is fine as a stopgap per-file fix in the meantime.

---

## Priority 4 — `AgentState` passed where a shared helper expects `dict[str, Any]` (~11 diagnostics)

Every LangGraph node that calls a shared state-reading helper hits this:
```
src/application/langgraph/nodes/control/final_response_node.py (x3)
src/application/langgraph/nodes/documents/document_details_node.py
src/application/langgraph/nodes/question_answering/answer_question_node.py
src/application/langgraph/nodes/question_answering/explore_document_node.py
src/application/langgraph/nodes/question_answering/retrieve_evidence_node.py
src/application/langgraph/nodes/question_answering/retry_retrieval_node.py
src/application/langgraph/nodes/research/create_research_plan_node.py
src/application/langgraph/nodes/research/evaluate_research_node.py
src/application/langgraph/nodes/research/execute_research_node.py
src/application/langgraph/nodes/research/research_summary_node.py
src/application/langgraph/nodes/research/synthesize_research_node.py
```
e.g. `resolve_selected_document(state)` / `result_from_state(state)` are declared to take `state: dict[str, Any]`, but every call site actually passes an `AgentState` (presumably a `TypedDict` subtype of `dict`, or a dataclass — worth confirming which). This is a parameter-type-too-narrow issue on the **shared helper side**, not a bug at each of the 11 call sites.

**Fix:** widen the shared helpers' parameter annotation from `dict[str, Any]` to `AgentState` (if `AgentState` genuinely is a `dict` subtype/TypedDict, this is a pure widening with no behavior change) — one edit per helper function, resolves all 11 call sites at once. Identify the helper module(s) (`resolve_selected_document`, `result_from_state`, `resolve_state_response_text`, `reflection_decision_from_state`, `generated_answer_text_from_state`) and fix their signatures rather than touching any of the 11 call sites.

---

## Priority 5 — `Sequence[X]` vs `list[X]` invariance at ORM/database boundaries (~15-20 diagnostics)

Python's `list[X]` is invariant, so a `Sequence[X]` (e.g. what SQLAlchemy's `.scalars().all()` returns) cannot satisfy a parameter typed `list[X]`, even though nothing is mutated:

```
src/infrastructure/db/repositories/extraction/extraction_reader.py (11 — task_rows, spare_part_rows, equipment_rows, manufacturer_rows, supplier_rows, ...)
src/infrastructure/db/repositories/document/document_graph_reader.py
src/infrastructure/db/repositories/memory/conversation_memory_repository.py
scripts/report_text_corruption_candidates.py
```

**Fix:** widen the receiving mapper/`to_domain(...)` function parameter types from `list[X] | None` to `Sequence[X] | None` — these functions only read the input, so this is a safe, mechanical widening with no behavior change. Do **not** fix by wrapping every call site in `list(...)`; that's a much larger, purely cosmetic diff for the same result.

---

## Priority 6 — Individually-confirmed bugs and annotation mistakes (investigate/fix one by one, not a single pattern)

These don't share a root cause — each was read directly and is reported here with its actual status, not a guess.

| File:Line | Finding | Status |
|---|---|---|
| `scripts/run_retrieval_quality_gate.py:15` | `PROJECT_ROOT = Path(__file__).resolve().parents[1]` — `Path` is used but never imported (only `argparse`, `sys` are). This executes at **module import time**. | 🔴 **Confirmed broken** — this script cannot currently run at all; crashes with `NameError` immediately. Fix: add `from pathlib import Path`. |
| `scripts/demo_agent_cli.py:84` | `def _build_visibility_policy(args) -> "DemoVisibilityPolicy":` — the forward-reference string can't resolve because `DemoVisibilityPolicy` is only imported **inside the function body** (L89), not at module or `TYPE_CHECKING` scope. | 🟡 Confirmed type-checking bug, not a runtime crash (the annotation is never evaluated at runtime unless something calls `typing.get_type_hints` on it). Fix: move the import into a module-level `if TYPE_CHECKING:` block. |
| `src/application/validation/classification/document_classification_validator.py:20` | `value.result.confidence_score < 0 or value.result.confidence_score > 1` — `confidence_score` is `float \| None`; no `None` guard. | 🟡 **Possible real bug** — will raise `TypeError` at runtime if `confidence_score` is ever `None`. Needs a product decision: is `None` a legitimate value here (add a guard) or should the domain field be tightened to non-Optional `float`? |
| `src/application/validation/extraction/extraction_result_validator.py:15` | Same shape, same file family, same question. | 🟡 Same as above. |
| `src/shared/execution/events/event_tracker.py:23` | `event_service: EventService = getattr(service_instance, "event_service", None)` — declared non-Optional, but the very next line does `if event_service is None: return`, proving the code itself expects `None`. | 🟢 Simple annotation-only bug. Fix: `event_service: EventService | None = ...`. |
| `src/application/agent_runtime/session/conversation_turn.py:15` | `def from_message(...) -> "ConversationTurn" \| None:` — invalid mixed quoted/unquoted union syntax. | 🟢 The file already has `from __future__ import annotations`, so quoting is unnecessary anywhere in it. Fix: `-> ConversationTurn | None:` (drop the quotes). |
| `src/application/workflows/retrieval/tracing/retrieval_trace_recorder.py:29-37` | `str \| None` passed to constructor params typed `float \| None` (`fused_score`) / `int \| None` (`dedup_group_size`). | 🟡 **Worth checking** — this isn't just an optionality mismatch, the base types disagree (`str` vs `float`/`int`). Check whether a value is being read as a raw string somewhere upstream without being parsed to a number first. |
| `src/application/orchestrator/ingestion/vector_runtime_builder.py:65,76,103(x2),122` | "Variable not allowed in type expression" — `QdrantClient` (and others) used as a return-type/parameter annotation while actually being a runtime-resolved variable (a different lazy-import mechanism than Priority 1's `__getattr__`, but the same underlying tension between deferred imports and static typing). | 🟡 Needs the same general remedy as Priority 1 — a `TYPE_CHECKING`-guarded static import of the *real* `QdrantClient` type for annotation purposes, separate from the runtime lazy-resolution path. |
| `src/application/workflows/ingestion/pipeline/stage_lifecycle/ingestion_stage_sequence_executor.py:99` | "Function with declared return type `IngestionResult` must return value on all code paths" — the `except Exception as exc: self.exception_handler.handle(...)` branch never explicitly returns, relying on `handle()` being declared `-> NoReturn`. | 🟡 Root cause: **every constructor parameter on this class is untyped** (`stage_lifecycle`, `duplicate_coordinator`, `exception_handler`, …), so pyright can't see `exception_handler`'s real type or its `NoReturn` signature. Fix: add type annotations to the constructor — this is a good representative example of a broader "many DI-heavy classes in this codebase have fully untyped constructors" pattern worth a dedicated follow-up if the team wants stronger type coverage generally (out of scope to enumerate exhaustively here). |
| `src/application/workflows/parsing/normalizers/docling_document_normalizer.py:215-216` | `.sort(key=lambda entry: entry[1].metadata.get("layout_page_order") if ... else entry[0])` — the lambda's return type is `Any \| int \| None`; `None` can't be compared with `<`. | 🟡 Real narrow-typing gap in this specific sort key, unrelated to the other patterns above. Fix: normalize the lambda's return type to always be `int` (fall back to `entry[0]` — already an `int` — instead of `None` in the falsy branch, or coerce explicitly). |

---

## Full file:diagnostic-count listing (for completeness / triage tracking)

Top 20 files by raw diagnostic count (several are already explained above; the rest are covered by Priority 1/3's patterns recurring within them):

```
33  src/application/langgraph/nodes/control/route_request_node.py
23  scripts/profile_graph_build.py
22  src/application/reporting/document_parsing/graph_build_profiling/graph_build_report_markdown_renderer.py
17  src/application/workflows/retrieval/deduplication/duplicate_group_builder.py
17  src/domain/assets/table_parallel_stream.py
16  src/application/workflows/parsing/builders/chunking/deduplication/chunk_payload_deduplicator.py
15  src/application/prompts/classification/document_classification_summary_builder.py
14  src/application/workflows/parsing/builders/chunking/builders/fragment/chunk_fragment_builder.py
13  src/application/workflows/classification/hybrid_document_type_resolver.py
11  src/application/workflows/question_answering/answer_pipeline/structured_fact_join/structured_evidence_scope_filter.py
11  src/application/workflows/question_answering/evidence/table_evidence_hydrator.py
11  src/domain/assets/table_cell_span.py
11  src/infrastructure/db/repositories/extraction/extraction_reader.py
 9  scripts/ask_document.py
 9  src/application/orchestrator/ingestion/parsing_runtime_builder.py
 8  src/application/workflows/parsing/tables/semantics/table_semantic_classifier.py
 7  src/application/agent_runtime/bootstrap/agent_service_builder.py
 7  src/application/services/answer_generation/__init__.py
 7  src/application/workflows/question_answering/__init__.py
 6  src/application/evaluation/retrieval/benchmarking/resolution/resolvers/retrieval_benchmark_dataset_resolver.py
```
(96 more files with 1-6 diagnostics each — all covered by one of the six priorities above; run the reproduction command below for the live, complete list at any time.)

**`src/application/langgraph/nodes/control/route_request_node.py` (33, the single largest file)** was not deep-dived above — a quick look shows the same "`object`-typed value from a loosely-typed state dict accessed without narrowing" shape as Priority 3, applied to LangGraph state reads (`Cannot access attribute "options" for class "object"` x 20+). Recommend folding its fix into whichever LangGraph state-typing work comes out of Priority 4 (both are "the shared state container is typed too loosely at its read boundary").

---

## Implementation plan

| Phase | Scope | Risk | Est. diagnostics resolved |
|---|---|---|---|
| **A** | Add `TYPE_CHECKING` static-import blocks to all 9 lazy `__getattr__` files (Priority 1) | None — zero runtime change | ~150-190 |
| **B** | Fix the confirmed broken/simple bugs: `run_retrieval_quality_gate.py` missing import, `demo_agent_cli.py` deferred import, `event_tracker.py` annotation, `conversation_turn.py` union syntax, `docling_document_normalizer.py` sort-key type | Low — small, isolated, mostly annotation-only edits | ~10 |
| **C** | Capture-to-local / `assert` fixes for the Optional-narrowing-across-closures cases (Priority 2) | None — additive narrowing only | ~10-15 |
| **D** | Team decision + fix: nullable `confidence_score` comparisons in the two validators; investigate the `str`→`float`/`int` mismatch in `retrieval_trace_recorder.py` | Needs a product/domain call before the fix, then low risk | ~8 |
| **E** | Widen shared helper parameter types: LangGraph node helpers (`dict[str, Any]` → `AgentState`, Priority 4) and ORM mapper functions (`list[X]` → `Sequence[X]`, Priority 5) | Low — pure type widening, no logic change | ~30 |
| **F** | `vector_runtime_builder.py`'s runtime-variable-as-type-annotation pattern; add type annotations to `IngestionStageSequenceExecutor.__init__` (and audit for the same pattern elsewhere if the team wants broader constructor typing) | Low-moderate | ~10 |
| **G** | Priority 3's `int()`/`float()`-on-`object` and dict-into-dataclass patterns — the largest remaining bucket (~110-140), but genuinely needs per-file judgment (what's the right coercion/validation shape for *this* metadata bag). Start with adding a general-purpose `coerce_int` alongside the existing `coerce_positive_int`/`coerce_float`, route the `from_dict`-style deserializers through it first (mechanical), then work through the dataclass-construction sites file by file. | Low per-edit, but high file count — budget as a multi-session follow-up | ~110-140 |
| **H** | Final long-tail cleanup: remaining one-off diagnostics not captured by A-G (re-run pyright after A-G to see what's actually left, rather than triaging the pre-fix list) | Case by case | remainder |

**Verification after every phase:** re-run the reproduction command below and diff the diagnostic count/file list against this document's baseline (429 errors / 34 warnings / 116 files), plus run the full `pytest tests/unit tests/integration` suite to confirm zero behavior regressions — every fix above is expected to be either purely additive (TYPE_CHECKING blocks, asserts) or a type-annotation widening, none should change runtime control flow except the Phase D items, which touch actual validation logic and need their own dedicated tests once the team decides the intended behavior.

### Reproduction command

```
npx --yes pyright --outputjson --pythonpath ./myenv/Scripts/python.exe src scripts > pyright_report.json
```
(drop `--outputjson` for the normal human-readable terminal output matching what Pylance shows inline in the editor.)
