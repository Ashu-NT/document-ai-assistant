# Concrete Implementation Plan: Table Classification Domain Split

Companion to `table_classification_domain_split_implementation_map.md` (the Phase 1 discovery
document — read that first for the full file-by-file trace this plan is grounded in). This document
is the Phase 2 execution plan: what to build, in what order, with what exact shape.

**Hard constraint carried over from the impact map (§16):** every new enum reuses the *exact* string
values `TableKind` already uses for `TableCategory`/`TableShape` — this is a type split, not a value
rename, because `ChunkType._chunk_type_from_table_category()` and every already-ingested document's
persisted `parser_extra`/`ChunkORM.table_category` row are pinned to those strings. `TableQueryStrategy`
is the one place values are free to change (never persisted), and that's deliberately deferred to a
separate sub-step (4b) so the risky part isn't bundled with the safe part.

---

## Step 1 — Cleanup: bare-string frozensets → `TableKind` references

**Decision, settled during implementation:** `TableCategory`/`TableShape` (and later `TableSignal`)
stay in `src/application/workflows/shared/` — the same package `table_kind.py` already lives in —
not relocated to `src/shared/`. The overwhelming majority of consumers are in the `workflows`
application layer, and `TableAsset.table_category`/`table_shape` are already plain `str | None`
fields at the domain layer (not typed as `TableKind` today), so the handful of domain-layer table-row
normalizers that bare-string-compare against category values (`specification_key_value_table_normalizer.py`,
`troubleshooting_table_normalizer.py`, `spare_parts_table_normalizer.py`,
`certification_particulars_table_normalizer.py`, `maintenance_schedule_table_normalizer.py`) simply
**stay on bare strings** — they never needed the enum type in the first place, since they already
work directly off the plain string field. This also means `TableSignal` in Step 5, once added as a
`TableAsset` field, needs its own explicit layering check at that point (it would be new, not
inherited from an existing plain-string field) — flagged there, not resolved here.

**This step, one file:**

**`src/application/workflows/question_answering/answer_context/tables/table_type_resolution_core.py`**
(already imports `TableKind` at line 6):

```python
_RECORD_TABLE_CATEGORIES = frozenset(
    {
        TableKind.TECHNICAL_DATA_TABLE,
        TableKind.OPERATING_LIMITS_TABLE,
        TableKind.CONNECTION_TABLE,
        TableKind.IDENTIFIER_TABLE,
        TableKind.OPERATION_REFERENCE_TABLE,
        TableKind.SENSOR_INSTRUMENT_TABLE,
    }
)
```

`category in _RECORD_TABLE_CATEGORIES` (line 98) still works unchanged — `TableKind` is a
`StrEnum`, and `category` is already lowercased to a plain `str` at line 70, so membership testing
against `TableKind` members compares equal to their string values with no cast needed.
`_RECORD_TABLE_CHUNK_TYPES` (line 22) stays as bare strings — `chunk_type` values come from
`ChunkType`, a different enum entirely, out of scope for this migration (impact map §15).

**`src/domain/assets/table_rows/specification_key_value_table_normalizer.py`'s `_APPLICABLE_CATEGORIES`
stays as bare strings, permanently** — it's a domain-layer file working directly off
`TableAsset.table_category: str | None`, which was never typed as `TableKind` to begin with. No fix
needed or planned here; this is intentional scope discipline, not a gap.

**Tests:** no new tests needed — this is a pure internal representation change with identical
runtime behavior (`TableKind` members equal their string values). Run
`test_table_type_resolution_core.py` unmodified to confirm.

---

## Step 2 — Introduce `TableCategory` and `TableShape`

**New file `src/application/workflows/shared/table_category.py`** (same package as `table_kind.py`):

```python
from enum import StrEnum


class TableCategory(StrEnum):
    """Single-valued semantic subject of a table, set once at parse time by
    `TableSemanticClassifier`. Independent of `TableShape` (structural
    organization) and `TableQueryStrategy` (QA-time routing) -- see
    table_classification_domain_split_implementation_map.md.
    """

    GENERAL_TABLE = "general_table"
    TOC_TABLE = "toc_table"
    MAINTENANCE_INTERVAL_TABLE = "maintenance_interval_table"
    TROUBLESHOOTING_TABLE = "troubleshooting_table"
    SPARE_PARTS_TABLE = "spare_parts_table"
    OPERATION_REFERENCE_TABLE = "operation_reference_table"
    OPERATING_LIMITS_TABLE = "operating_limits_table"
    TECHNICAL_DATA_TABLE = "technical_data_table"
    CERTIFICATION_TABLE = "certification_table"
    CONNECTION_TABLE = "connection_table"
    SENSOR_INSTRUMENT_TABLE = "sensor_instrument_table"
    IDENTIFIER_TABLE = "identifier_table"
```

12 members — the exact reachable output set of `TableSemanticClassifier.classify()` (impact map
§4a), same spellings, same values. No member is added or removed.

**New file `src/application/workflows/shared/table_shape.py`** (same package as `table_kind.py`):

```python
from enum import StrEnum


class TableShape(StrEnum):
    """Single-valued structural organization of a table, set once at parse
    time by `TableStructureSummaryBuilder`. `None` on `TableAsset.table_shape`
    means no summarizer matched -- there is no catch-all member here by
    design, matching current behavior exactly.
    """

    RECORD_TABLE = "record_table"
    MAINTENANCE_SCHEDULE_MATRIX = "maintenance_schedule_matrix"
    SPECIFICATION_MATRIX = "specification_matrix"
    PERFORMANCE_CURVE_MATRIX = "performance_curve_matrix"
```

4 members — the exact reachable output set of `TableStructureSummaryBuilder.build()` (impact map
§4b).

### Producer updates (parse-time — behavior-preserving type change only)

- **`table_semantic_classifier.py`**: change the `TableKind` import to `TableCategory`; change every
  `TableKind.X` return value (lines 94-167) to `TableCategory.X`; change `classify()`'s return
  type annotation from `tuple[TableKind, float]` to `tuple[TableCategory, float]`.
- **`table_semantic_rule_evaluator.py`, `table_specification_rule_evaluator.py`,
  `table_structured_list_classifier.py`**: no changes — these files never import `TableKind`, they
  only return `bool` from `looks_like_*` methods.
- **`table_structure_summary.py`**: change `TableStructureSummary.table_shape: TableKind` to
  `table_shape: TableShape`.
- **The 4 structure summarizers** (`generic_record_structure_summarizer.py`,
  `maintenance_schedule_structure_summarizer.py`, `specification_matrix_structure_summarizer.py`,
  `performance_curve_structure_summarizer.py`): change `TableKind` import to `TableShape`; change
  each summarizer's single `TableKind.X` construction to `TableShape.X`.
- **`table_semantic_resolver.py`**: no signature changes needed — `category.value`/
  `structure_summary.table_shape.value` (lines 48, 53) already extract the plain string before
  assigning to `TableAsset.table_category`/`table_shape` (which stay `str | None`, unchanged). This
  file's behavior is identical whether `category` is a `TableKind` or a `TableCategory` instance.

### Consumer updates — persistence/chunking (impact map §5)

None of these files need behavioral changes — `TableAsset.table_category`/`table_shape` and
`DocumentChunk.table_category`/`table_shape` are already `str | None`, not `TableKind`, all the way
through `ChunkFragment` → `ChunkPayload` → `ChunkORM` → `RetrievedChunk.metadata`. This whole chain
reads/writes plain strings today and continues to after Step 2 — **no file in §5 needs to change for
Step 2**, because the type split happens entirely upstream of where these strings enter the pipeline.
Verify this assumption holds by running the full persistence/chunking test suite after Step 2 lands
(§5's ~15 test files) with zero edits — if any fail, that reveals a spot that actually depended on
`TableKind` import identity rather than string value, and needs individual attention.

### Consumer updates — QA-time bare-string sweep (impact map §11)

**Domain-layer normalizers are explicitly out of scope**, per Step 1's settled decision:
`troubleshooting_table_normalizer.py:110`, `spare_parts_table_normalizer.py:117,119`,
`certification_particulars_table_normalizer.py:27`, `maintenance_schedule_table_normalizer.py:42`,
and `specification_key_value_table_normalizer.py`'s `_APPLICABLE_CATEGORIES` all stay as bare
strings permanently — they work directly off `TableAsset.table_category: str | None` and live in
`src/domain/`, which must not import from `src/application/workflows/shared/`.

For the remaining, application-layer-only sites: each dangerous bare-string site becomes a
`TableCategory.X.value` or plain string comparison (unchanged runtime behavior either way, since
`StrEnum` members compare equal to their string value) — but **prefer importing `TableCategory`/
`TableShape` and comparing against the enum member** wherever the file doesn't already have a reason
to stay string-only, closing the exact gap the literal-sweep in §11 flagged:

| File | Change |
|---|---|
| `table_fragment_builder.py:257-267` (`_chunk_type_from_table_category`) | compare against `TableCategory.X` — **do not change the `ChunkType` values it returns** (impact map §15) |
| `context_filtering_guardrail.py:255-256` | `== TableCategory.SPARE_PARTS_TABLE.value` (reads from a `dict[str,str]` metadata bag, so `.value` needed explicitly, or compare `TableCategory(table_category) == TableCategory.SPARE_PARTS_TABLE` guarded by try/except for old-record safety) |
| `spare_parts_table_parser.py:209,211,213` | same pattern (lines 209/211 only — line 213 compares `chunk_type`, out of scope, leave as-is) |
| `prompt_evidence_role_assigner.py:37,42` | **correction: these are `chunk_type` values, not `table_category`** (the `_PREFERRED_CHUNK_TYPES` dict is checked against `source.chunk_type` at line 100) — **not in scope**, leave as-is |
| `spare_parts_evidence_relevance_detector.py:23` | compares against `chunk_type`, a `ChunkType` value — **not in scope**, leave as-is |
| `retrieved_chunk_signature.py:37`, `chunk_payload_signature.py:39` | compare against `chunk_type.value`, a `ChunkType` value — **not in scope**, leave as-is |
| `prompt_table_type_detector.py:57` | `== TableCategory.TECHNICAL_DATA_TABLE.value` (already reads from a lowercased plain string at line 34-36) |

**Do not touch** any site comparing against a `ChunkType` value (`spare_parts_evidence_relevance_detector.py`,
`retrieved_chunk_signature.py`, `chunk_payload_signature.py`, `table_fragment_builder.py`'s
`_TABLE_LIKE_CHUNK_TYPES`-style sets if any) — those are a different enum, already out of scope.

### New tests

- `tests/unit/application/workflows/shared/test_table_category.py`,
  `test_table_shape.py` (new, minimal — assert member count and that every value matches the
  corresponding `TableKind` value it replaces, as a regression guard against accidental respelling).
- Extend `test_table_semantic_classifier.py` to assert `classify()` returns `TableCategory`
  instances (`isinstance(category, TableCategory)`), not just correct values.
- Extend `test_table_structure_summary_builder.py` similarly for `TableShape`.
- Run every test file listed in impact map §9's "direct `TableKind` importers" list — update their
  imports to `TableCategory`/`TableShape` as appropriate; no assertion values should need to change.

---

## Step 3 — Migrate persistence/chunking imports

Per Step 2's finding, this step may turn out to be **a no-op** for behavior — but every file in
impact map §5 that currently has `from src.application.workflows.shared.table_kind import TableKind`
in its import block (even if unused after inspection, or used only for a type hint on a variable that
is immediately `.value`'d) should be swept and corrected to avoid a stale import once `table_kind.py`
is deleted in Step 6. Grep `src/infrastructure/db/`, `.../chunking/builders/fragment/`, and
`.../builders/document_graph/` for `table_kind` (module or class name) before starting Step 6, not
during it.

No new tests — this step is import hygiene, covered by existing tests continuing to pass.

---

## Step 4a — Extract `TableQueryStrategy` (same values, new type)

**New file `src/application/workflows/question_answering/answer_context/tables/table_query_strategy.py`**
(placed beside `table_type_resolution_core.py`, matching this repo's existing layering — confirmed by
the impact map that `prompts/` → `workflows/answer_context/` is the established one-way import
direction, not the reverse):

```python
from enum import StrEnum


class TableQueryStrategy(StrEnum):
    """QA-time-only resolution of "how should this specific table be
    answered," derived from category + shape + chunk_type + header/row
    content signals. Never persisted -- recomputed per query against
    `AnswerTable`/`PromptSourceView`. Not an intrinsic property of the
    table itself; see table_classification_domain_split_implementation_map.md
    section 0 for why this was previously conflated with TableCategory/TableShape.
    """

    GENERAL_TABLE = "general_table"
    RECORD_TABLE = "record_table"
    KEY_VALUE_TABLE = "key_value_table"
    TOC_TABLE = "toc_table"
    TROUBLESHOOTING_TABLE = "troubleshooting_table"
    SPARE_PARTS_TABLE = "spare_parts_table"
    CERTIFICATION_TABLE = "certification_table"
    MAINTENANCE_SCHEDULE_TABLE = "maintenance_schedule_table"
    MAINTENANCE_SCHEDULE_MATRIX = "maintenance_schedule_matrix"
    SPECIFICATION_MATRIX = "specification_matrix"
    PERFORMANCE_CURVE_MATRIX = "performance_curve_matrix"
```

11 members, identical values to the `TableKind` subset `resolve_table_type()` currently returns
(impact map §4c) — this step is a rename of the *type*, not the *vocabulary*. `PERFORMANCE_CURVE_MATRIX`
is included even though it's only reachable via the shape-passthrough branch (line 83), since it's a
genuine reachable output of the function.

**`table_type_resolution_core.py` changes:**
- Import `TableCategory`, `TableShape`, `TableQueryStrategy` instead of `TableKind`.
- `resolve_table_type()`'s return type becomes `tuple[TableQueryStrategy, dict[int, str]]`.
- Every `TableKind.X` construction (lines 75-104) becomes `TableQueryStrategy.X`.
- Line 81-86's `shape == "maintenance_schedule_matrix"` etc. become
  `shape == TableShape.MAINTENANCE_SCHEDULE_MATRIX.value` (or keep as bare strings — `shape` is
  already lowercased via `.strip().lower()` at line 71, so no behavior change either way; prefer the
  enum reference per the same closing-the-gap rationale as Step 2).
- Line 88-97's `category == "toc_table"` etc. similarly become `TableCategory.X.value` comparisons.
- `_RECORD_TABLE_CATEGORIES` (already fixed in Step 1) needs no further change.

**`answer_table_schema_inferer.py`**: change `_RESOLVED_TYPE_TO_ANSWER_KIND` (lines 8-20) to key off
`TableQueryStrategy` instead of `TableKind` — same 7 string values on the right-hand side, no change
to `infer()`'s own return type (still `tuple[str, dict[int,str]]`, since this is the boundary where
the new typed strategy gets mapped back down to the plain-string vocabulary
`AnswerTable.table_kind`/the 5 downstream consumers already expect).

**`prompt_table_type_detector.py`**: same treatment for `_RESOLVED_TYPE_TO_PROMPT_LABEL` (lines
11-23), plus its 5 residual string-literal heuristics (lines 57-69) stay untouched (they operate on
plain strings already, no `TableKind` involvement).

**`AnswerTable`/`AnswerTableProjection`**: no change in Step 4a — `table_kind: str` stays a plain
string field, since both `AnswerTableSchemaInferer` and the 6 projection builders (impact map §4d)
continue producing plain strings from their existing mapping dicts. The type-safety win of Step 4a is
entirely inside `resolve_table_type()`'s internals and its two direct callers; it does not yet
propagate to `AnswerTable.table_kind` or its 3 downstream branchers
(`SpecificationTableKeyValueExtractor`, `MaintenanceTableCandidateExtractor`, `TroubleshootingRenderer`)
— that's Step 4b.

### New tests

- Rename/extend `test_table_type_resolution_core.py`'s `TableKind × TableKind` parametrization to
  `TableCategory × TableShape` (the actual input space) asserting a `TableQueryStrategy` output —
  this is a more accurate parametrization than the current one, which iterates the return type
  rather than the input types.
- No new test files — `answer_table_schema_inferer.py`/`prompt_table_type_detector.py`'s existing
  tests should pass unmodified (output strings unchanged).

---

## Step 4b (optional, separate PR) — Type `AnswerTable.table_kind` as `TableQueryStrategy`

This is the deeper win the original proposal envisions (renaming the field itself, not just its
producer), deliberately separated from 4a because it touches 3 behavior-branching consumers instead
of 2 pure-mapping ones:

- `AnswerTable.table_kind: str = "general_table"` → `table_kind: TableQueryStrategy = TableQueryStrategy.GENERAL_TABLE`
  (`answer_table.py:24`); same for `AnswerTableProjection.table_kind` (`answer_table_projection.py:11`).
- Each of the 6 `*_projection_builder.py` files' `table_kind="record_table"`-style literals (impact
  map §4d table) becomes `table_kind=TableQueryStrategy.RECORD_TABLE`.
- `SpecificationTableKeyValueExtractor._iter_key_values()` (lines 67-84): `.startswith("maintenance_")`
  becomes `table.table_kind in {TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE, TableQueryStrategy.MAINTENANCE_SCHEDULE_MATRIX}`;
  the three `==` checks become enum-member comparisons.
- `MaintenanceTableCandidateExtractor.extract()` (lines 28-33): same treatment.
- `TroubleshootingRenderer` (line 72): same treatment — this file currently has **no** `TableKind`/
  enum import at all (bare string only), so this is a net new import, not a swap.

**Do not fold this into Step 4a.** The impact map's own reasoning (§4d) is that this field is
*already functioning* as a query strategy today, just typed as `str` — re-typing it is safe
(behavior-preserving) but touches enough call sites that it deserves its own test run and its own
review, not to be buried inside the bigger Step 4a diff.

### New tests

- Extend each `*_projection_builder.py`'s existing test to assert `isinstance(result.table_kind, TableQueryStrategy)`.
- Extend `test_specification_table_key_value_extractor.py`, the maintenance-candidate-extractor
  test, and `test_troubleshooting_renderer.py` similarly.

---

## Step 5 — Introduce `TableSignal` (greenfield, most design latitude)

Unlike Steps 2-4, there is no existing single-valued field to split — `TableSignal` generalizes two
things that today only exist as *behavior*, not *data*:

1. `resolve_table_type()`'s `column_roles: dict[int, str]` byproduct (task/interval/label/value/notes
   roles, impact map §4c step 1) — already multi-valued, already per-column, just not exposed as a
   named signal set at the table level.
2. The classifier's `looks_like_*` rule outcomes (impact map §4a) — currently **discarded** the
   moment `TableSemanticClassifier.classify()` picks its first match and returns; a table that
   matches `looks_like_spare_parts_table` AND incidentally contains identifier-like columns loses the
   second fact entirely today.

**New file `src/application/workflows/shared/table_signal.py`** (same package as `TableCategory`/
`TableShape`/`table_kind.py` — see Step 1's settled decision on package location):

```python
from enum import StrEnum


class TableSignal(StrEnum):
    """Multi-valued content characteristics detected in a table. Unlike
    TableCategory/TableShape (exactly one value each), a table can carry
    any number of signals simultaneously. Populated from classifier rule
    outcomes that would otherwise be discarded once TableCategory is
    decided.
    """

    IDENTIFIERS = "identifiers"
    SPECIFICATIONS = "specifications"
    OPERATING_LIMITS = "operating_limits"
    MAINTENANCE_INTERVALS = "maintenance_intervals"
    SCHEDULES = "schedules"
    TROUBLESHOOTING = "troubleshooting"
    SPARE_PARTS = "spare_parts"
    CERTIFICATION = "certification"
    CONNECTIONS = "connections"
    SENSOR_DATA = "sensor_data"
    PERFORMANCE_DATA = "performance_data"
```

**Two design decisions settled during implementation, both deliberate deviations from the draft
above:**

1. **`TableAsset.signals` is typed `frozenset[str]`, not `frozenset[TableSignal]`.** `TableAsset`
   lives in `src/domain/`, and `TableSignal` lives in `src/application/workflows/shared/` (per Step
   1's settled package-location decision) — a domain field cannot be typed with an application-layer
   enum without violating layering. Rather than relocate `TableSignal` (which would put it out of
   step with `TableCategory`/`TableShape`'s established location), `TableAsset.signals` follows the
   exact precedent already set by `table_category: str | None`/`table_shape: str | None` on the same
   dataclass: plain-typed at the domain layer, enum-typed only where classification logic actually
   runs (`TableSemanticClassifier`, `TableSemanticResolver`). `TableSemanticResolver.resolve()`
   converts `TableSignal` members to their `.value` strings before assigning, exactly as it already
   does for `table.table_category = category.value`.

2. **`TableSemanticClassifier.classify()`'s signature is unchanged.** Rather than widening its return
   type to a 3-tuple (which would have broken all ~15 existing call sites in
   `test_table_semantic_classifier.py` for zero test benefit, since none of them assert on signals),
   a new, separate `detect_signals()` method was added. Both methods share a `_build_context()`
   private helper that does the row/header/text preparation once, so there's no duplicated logic —
   only the rule-evaluation loop differs (first-match-and-return for `classify()`, evaluate-every-rule
   for `detect_signals()`). This is a cleaner separation of concerns than the original draft's
   "still returned separately" phrasing implied, and it means `classify()`'s existing 15 tests needed
   zero changes.

3. **The `column_roles` → `TableSignal` open question (originally flagged as unresolved) is settled:
   `column_roles` stays QA-time-only, never merged into the persisted signal set.** It's fundamentally
   a different kind of fact (per-column role, recomputed per query from headers) than `TableSignal`
   (per-table content characteristic, computed once at parse time from the classifier's rule
   evaluations) — conflating them would reintroduce exactly the kind of "different axis, same bucket"
   problem this whole migration exists to fix.

**Implemented, minimal first cut:**

- `detect_signals()` evaluates every classifier rule unconditionally (no short-circuit) and maps each
  `looks_like_*` hit to one or more `TableSignal` members (the three maintenance-interval-related
  rules — matrix detector, `looks_like_maintenance_interval_table`, `looks_like_lubrication_schedule_table`
  — all map to *both* `MAINTENANCE_INTERVALS` and `SCHEDULES`, since a maintenance-interval table is
  definitionally also a schedule; every other rule maps to exactly one signal). `TOC_TABLE`,
  `OPERATION_REFERENCE_TABLE`, and `GENERAL_TABLE` have no signal analog and contribute none — this
  matches the given `TableSignal` vocabulary exactly, no new signal values were invented.
- `TableAsset.signals: frozenset[str] = frozenset()` (new field, additive, defaults empty).
- Wired through `TableSemanticResolver.resolve()` immediately after the existing `classify()` call,
  mirrored into `parser_extra["table_signals"]` as a sorted list of strings (same JSON-blob pattern
  as every other field on this class — no DB migration).
- `PERFORMANCE_DATA` is defined in the enum but not yet wired to any rule in this pass — it belongs
  to the shape side (`PerformanceCurveStructureSummarizer`), which this pass didn't touch, matching
  "explicitly deferred" below.

**Explicitly deferred, not attempted in this pass:** full coverage of every classifier rule as a
signal, retrofitting `TableSignal` into the retrieval-filtering guardrails/dedup-fingerprint sites
listed in impact map §7 (those currently work directly off `table_category`/`chunk_type` and have no
proven need for multi-valued signals yet — adding them speculatively would violate the "no
hypothetical future requirements" constraint).

### New tests

- `test_table_signal.py` (new).
- Extend `test_table_semantic_classifier.py` with cases asserting multiple signals detected
  simultaneously (the exact scenario `TableCategory`'s single-valued design cannot express) —
  this is the one place in the whole migration where a genuinely new capability, not just a type
  split, should have a test proving it.
- Extend `test_table_asset.py` for the new `signals` field default/settable.
- Extend `test_parsed_asset_factory.py`/`test_document_graph_asset_rehydrator.py` for the
  `parser_extra["table_signals"]` round-trip, mirroring the pattern already established for
  `layout_region_id` etc. this session.

---

## Step 6 — Delete `table_kind.py`

Only after Steps 1-5 (or 1-4a, if 4b/5 are deferred to later PRs) are complete, every import is
migrated (verified via a final repo-wide grep for `table_kind` returning zero hits outside this
plan/the impact map's own historical references), and the full test suite is green. Delete the file
outright — no facade, no re-export shim, per this repo's standing no-facade convention.

---

## Step 7 — Full verification

After every step above: run the complete unit + integration suite (not just the touched files),
matching this session's established pattern for every prior phase. Any newly-introduced import cycle
(§ layering direction check in Step 1/2) would surface as a collection-time `ImportError`, not a test
failure — watch for that specifically since it won't show up as a familiar red assertion.

---

## Summary of sequencing risk, restated

| Step | Risk | Reversible mid-way? |
|---|---|---|
| 1 | None | Yes, trivially |
| 2 | None (proven value-disjoint) | Yes — new files are additive until producers switch over |
| 3 | None (import hygiene) | Yes |
| 4a | Low (type rename, same values, 2 callers) | Yes |
| 4b | Low-medium (3 behavior-branching consumers) | Yes, but needs its own test pass |
| 5 | Medium (genuinely new capability + one open design question) | Yes — additive field, can ship partially |
| 6 | None if 1-5 verified | No — do last |

Recommend landing 1, 2, 3, 4a as one PR (mechanical, low-risk, high test coverage already exists),
4b as a second PR, and 5 as a third PR with its own design sign-off on the open question above before
writing code.
