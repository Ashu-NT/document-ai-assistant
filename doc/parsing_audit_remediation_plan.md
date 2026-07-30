# Parsing Pipeline — Enterprise Audit & Remediation Plan

Audience: engineers touching `src/application/workflows/parsing/`, `src/infrastructure/parsing/`, and the ingestion pipeline. This document summarizes an architecture audit of the document-parsing subsystem against standard enterprise document-AI practice (multi-format support, resilience to untrusted input, observability, idempotency, RAG-quality extraction), and gives a concrete, file-mapped implementation plan to close the gaps.

The extraction core itself (table-family resolution, multi-column reading order, section-hierarchy fallback chain, profile-driven chunking) is solid and is **not** in scope for rework. Everything below is about failure handling, observability, and layering discipline at the edges of that core.

---

## How to read this document

Each finding has:
- **Problem** — what's wrong, evidenced with file:line.
- **Why it matters** — the enterprise practice it violates and the concrete failure scenario for our use case (multi-team, shipyard technical documents).
- **Affected files** — every file touched, new or existing.
- **Fix** — approach, with a code sketch where the shape of the fix is unambiguous. Sketches are illustrative, not final diffs — write real tests against them.

Findings are grouped into four phases, ordered by risk. Do them in order; later phases assume earlier ones landed.

---

## Phase 1 — Availability & input safety (do first)

These are the findings that can take down ingestion for every team, not just degrade quality for one document.

### 1.1 No timeout anywhere in the parsing/OCR path

**Problem**: `DoclingParser.parse()` (`src/infrastructure/parsing/docling/docling_parser.py:45`) calls `converter.convert(file_path, **conversion_kwargs)` synchronously with no wall-clock bound. There is no `signal.alarm`, `asyncio.wait_for`, or `concurrent.futures` timeout anywhere in `src/application/workflows/parsing/` or `src/infrastructure/parsing/`. `signal.alarm` isn't usable here anyway — this runs on Windows (`win32`), where `SIGALRM` doesn't exist.

**Why it matters**: a single pathological PDF (deeply nested layout, huge image, OCR-hostile scan) can hang a worker indefinitely. The batch script (`scripts/ingest_document_batch_support.py`) has no timeout either, so one bad file in a folder of 200 shipyard manuals blocks the rest. This is the top availability risk for a multi-team ingestion service.

**Affected files**:
- `src/infrastructure/parsing/docling/docling_parser.py` (wrap the `convert()` call)
- `src/config/settings/ingestion_settings.py` (new `parse_timeout_seconds` setting)
- `src/application/orchestrator/ingestion/ingestion_input_limits.py` (thread the setting through)
- `src/application/orchestrator/ingestion/parsing_runtime_builder.py` (pass timeout into `DoclingParser`)
- `src/shared/exceptions/ingestion_exceptions.py` (new `DocumentParsingTimeoutError`)

**Fix**: run the blocking `convert()` call in a worker thread and bound it with `Future.result(timeout=...)` — this works cross-platform, unlike `signal`. Docling's converter isn't cancellable mid-call, so this bounds *our* wait, not Docling's internal work; the orphaned thread is abandoned (acceptable — the process should alert/restart on repeated timeouts rather than pretend to cancel uncancellable C-extension work).

```python
# src/infrastructure/parsing/docling/docling_parser.py
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

class DoclingParser:
    def __init__(self, ..., timeout_seconds: float | None = None) -> None:
        ...
        self.timeout_seconds = timeout_seconds

    def parse(self, file_path: str, *, enable_ocr_override: bool | None = None) -> RawParsedDocument:
        try:
            converter = ...
            conversion_kwargs: dict[str, Any] = {"raises_on_error": True}
            ...
            conversion_result = self._convert_with_timeout(converter, file_path, conversion_kwargs)
            ...
        except DocumentParsingError:
            raise
        except FutureTimeoutError as exc:
            raise DocumentParsingTimeoutError(
                f"Docling conversion exceeded {self.timeout_seconds}s.",
                details={"file_path": file_path, "timeout_seconds": self.timeout_seconds},
            ) from exc
        except Exception as exc:
            raise DocumentParsingError(...) from exc

    def _convert_with_timeout(self, converter: Any, file_path: str, kwargs: dict) -> Any:
        if self.timeout_seconds is None:
            return converter.convert(file_path, **kwargs)
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(converter.convert, file_path, **kwargs)
            return future.result(timeout=self.timeout_seconds)
```

`DocumentParsingTimeoutError` should extend `DocumentParsingError` so existing `except DocumentParsingError` call sites keep working unchanged, and so the exception handler in `ingestion_exception_handler.py` (Phase 1.4 territory — already isolates per document) treats it the same as any other parse failure: rollback, mark `IngestionRun` `FAILED`, structured error, no crash of the batch.

Add the setting the same way `max_file_size_mb`/`max_pdf_pages` already exist:

```python
# src/config/settings/ingestion_settings.py
parse_timeout_seconds: int = Field(alias="PARSE_TIMEOUT_SECONDS", default=600)
```

---

### 1.2 File content is trusted by extension only

**Problem**: `IngestionRequestValidator.validate()` (`src/application/validation/ingestion/ingestion_request_validator.py:57-63`) checks `resolved_path.suffix.lower() in {".pdf"}` and nothing else. No magic-byte/header check. A file renamed to `.pdf` that is anything else is handed straight to Docling.

**Why it matters**: enterprise ingestion of user-submitted files should never trust a client-controlled filename for content-type decisions — this is a standard OWASP file-upload control (unrestricted-file-upload mitigation), independent of whether the immediate failure mode is "just" a crash vs. something worse.

**Affected files**:
- `src/application/validation/ingestion/ingestion_request_validator.py`

**Fix**: no new dependency needed — PDFs always start with the 5-byte magic `%PDF-`.

```python
# src/application/validation/ingestion/ingestion_request_validator.py
_PDF_MAGIC_BYTES = b"%PDF-"

def _has_pdf_signature(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(len(_PDF_MAGIC_BYTES)) == _PDF_MAGIC_BYTES
    except OSError:
        return False

# inside validate(), after the extension check:
if extension in _SUPPORTED_INGESTION_EXTENSIONS and not _has_pdf_signature(resolved_path):
    result.add_issue(
        "file_path",
        "File content does not match a PDF signature.",
        "ingestion.file_path.content_mismatch",
    )
```

---

### 1.3 Parser has no port/interface — every other infra dependency does

**Problem**: `src/application/contracts/` has protocols for AI, retrieval, document, extraction, classification, audit, events, memory, and OCR (`OCRProvider`, `src/application/contracts/ai/ocr_provider.py` — a 3-line `Protocol`). There is no `parsing/` subpackage. `ParsingWorkflow.__init__` (`parsing_workflow.py:39`) type-hints the concrete class `DoclingParser` directly, and `parsing_runtime_builder.py:51-55` constructs it by name.

**Why it matters**: for a multi-team codebase meant to outlive one parsing library, every other integration point is swappable and testable via `Protocol` + fakes; parsing is the one exception. This is real vendor lock-in and an inconsistency a new team member will trip over.

**Affected files**:
- `src/application/contracts/parsing/__init__.py` (new)
- `src/application/contracts/parsing/parser_port.py` (new)
- `src/application/workflows/parsing/parsing_workflow.py` (type hint only — no behavior change)
- `src/infrastructure/parsing/docling/docling_parser.py` (no change needed if it already structurally satisfies the protocol — verify signature match)
- Tests currently constructing fake parsers for `ParsingWorkflow` (`tests/unit/application/workflows/parsing/_test_parsing_workflow_part1.py`, `_part2.py`) — no changes required, `Protocol` is structural, but worth confirming fakes still type-check under the new annotation.

**Fix**: mirror the existing `OCRProvider` pattern exactly.

```python
# src/application/contracts/parsing/parser_port.py
from typing import Protocol

from src.application.workflows.parsing.raw_parsed_document import RawParsedDocument


class ParserPort(Protocol):
    parser_name: str
    parser_version: str | None

    def parse(
        self,
        file_path: str,
        *,
        enable_ocr_override: bool | None = None,
    ) -> RawParsedDocument:
        ...
```

```python
# src/application/workflows/parsing/parsing_workflow.py
from src.application.contracts.parsing.parser_port import ParserPort

class ParsingWorkflow:
    def __init__(self, parser: ParserPort, ...) -> None:
        ...
```

This is a type-only change with near-zero blast radius (structural typing means `DoclingParser` already satisfies it) — it's cheap and should land alongside 1.1's timeout parameter so the port's shape includes anything the timeout work adds.

---

### 1.4 One bad element aborts the entire document, not just that element

**Problem**: `DoclingDocumentNormalizer.normalize()` (`normalizers/docling_document_normalizer.py:60-149`) wraps the *entire* per-item loop (lines 75-140) in one `try/except`. Any exception raised while processing a single Docling item (a malformed table, an unexpected provenance shape) propagates out of the whole method and aborts the whole document's parse — there is no per-item isolation, unlike the OCR fallback path (`page_ocr_fallback_workflow.py`) which already does this correctly per-target.

**Why it matters**: for a 400-page shipyard manual, one malformed page/element currently means zero pages get ingested. Enterprise document pipelines processing large technical manuals typically degrade gracefully: skip/flag the bad element, keep the other 399 pages, surface a warning.

Note the actual Docling `converter.convert()` call itself (1.1) is opaque/atomic — we can't isolate failures *inside* Docling's own conversion without forking the library. This fix targets the part we do control: our own per-item normalization loop, which is where partial-document salvage is realistically achievable today.

**Affected files**:
- `src/application/workflows/parsing/normalizers/docling_document_normalizer.py`
- `src/application/workflows/parsing/parsing_workflow_result.py` (no schema change — reuses existing `parse_warnings: list[str]`)
- `src/application/workflows/parsing/parsing_workflow_metrics.py` (optional: fold "N elements skipped due to normalization errors" into `collect_parse_warnings`)

**Fix**:

```python
# normalizers/docling_document_normalizer.py
def normalize(self, raw_parsed_document, document_id):
    raw_document = raw_parsed_document.raw_document
    items = list(self.item_extractor.iter_items(raw_document))
    normalized: list[ParsedCanonicalElement] = []
    skipped_item_errors: list[str] = []
    caption_extractor = DoclingCaptionExtractor(raw_document, items=items)
    layout_metadata_by_element_ref = self.layout_metadata_builder.build(...)

    for index, item in enumerate(items, start=1):
        if self.item_extractor.should_skip(item):
            continue
        try:
            element = self._build_canonical_element(
                item=item, index=index, document_id=document_id,
                raw_document=raw_document, caption_extractor=caption_extractor,
                layout_metadata_by_element_ref=layout_metadata_by_element_ref,
            )
        except Exception as exc:  # one item's failure must not sink the document
            skipped_item_errors.append(f"item {index}: {exc}")
            continue
        normalized.append(element)

    if not normalized:
        # every item failed — this is a real parse failure, not a partial result
        raise DocumentNormalizationError(
            "Docling normalization produced zero usable elements.",
            details={"item_count": len(items), "errors": skipped_item_errors[:10]},
        )

    reordered = self._apply_multi_column_reading_order(normalized)
    result = self.text_grid_table_fallback_applier.apply(reordered)
    self._last_skipped_item_errors = skipped_item_errors  # surfaced via a getter, folded into parse_warnings
    return result
```

The per-item body (lines 82-140 today) moves into `_build_canonical_element` unchanged — this is a pure extract-method refactor, not new logic. `skipped_item_errors` needs a way to reach `build_parsing_workflow_result` (either return a small result object instead of a bare list, e.g. `NormalizationOutcome(elements=..., item_errors=...)`, or thread it through `ParsingWorkflow.parse()` similarly to how `ocr_trace.warnings` already flow into `parse_warnings` today at `parsing_workflow_result_builder.py:36-41`). Prefer the explicit return-object over a stateful `_last_skipped_item_errors` attribute shown above — the attribute is there only to keep the sketch short.

---

## Phase 2 — Data quality & governance

These findings mean the pipeline already computes the right signals but throws them away. This phase is about wiring existing plumbing through, not inventing new plumbing.

### 2.1 `parse_confidence` is computed and never read

**Problem**: `compute_parse_confidence()` (`parsing_workflow_metrics.py:1-11`) produces a real heuristic score. Grep for consumers: only `parsing_workflow_result_builder.py` (computes it) and the offline `parsing_report_builder.py` (copies it into a debug report). Nothing gates on it.

**Why it matters**: a low-confidence parse (mostly orphaned elements, no sections) currently flows into classification → extraction → retrieval exactly like a clean parse. Teams get bad answers with no signal pointing back at "this document parsed badly."

**Affected files**:
- `src/config/settings/ingestion_settings.py` (new threshold setting)
- `src/application/workflows/ingestion/pipeline/stage_lifecycle/ingestion_stage_sequence_executor.py` (`_run_parsing`, around line 260, right where `parse_warnings` is already collected)
- `src/application/workflows/ingestion/models/ingestion_status.py` (new status, e.g. `COMPLETE_LOW_CONFIDENCE`, if you want it visible in status rather than just a warning)

**Fix** — start with visibility, not hard-blocking (a hard block on a heuristic score is its own risk: false positives block real ingestions). Fold it into the existing warnings path first:

```python
# src/application/workflows/ingestion/pipeline/stage_lifecycle/ingestion_stage_sequence_executor.py
# inside _run_parsing, right after: warnings.extend(parsing_result.parse_warnings)
if (
    parsing_result.parse_confidence is not None
    and parsing_result.parse_confidence < ingestion_settings.low_confidence_parse_threshold
):
    warnings.append(
        f"Low parse confidence ({parsing_result.parse_confidence:.2f}); "
        "review this document's extraction quality before relying on it."
    )
```

Once 2.2 (below) makes warnings actually visible to teams, revisit whether a hard gate (route to a `NEEDS_REVIEW` status instead of `COMPLETE`) is warranted — that's a product decision, not just an engineering one, since it changes what "successfully ingested" means.

### 2.2 `parse_warnings` never leave process memory

**Problem**: warnings collected in `_run_parsing` (`ingestion_stage_sequence_executor.py:260`) flow into `IngestionResult.warnings` and are returned to the immediate caller. No logging, no DB write, no dashboard. The only persistence path (`ParsingReportWriter` → `outputs/debug_parsing/*.json`) is only reachable from the manual `scripts/debug_parse_document.py`, not live ingestion.

**Why it matters**: for multiple teams ingesting documents asynchronously (batch jobs, scheduled ingestion), nobody is watching the synchronous return value. Today, the only way to find out *why* a document parsed badly is to re-run a debug script from scratch against the original file — if that file isn't retained, the information is gone permanently.

**Affected files**:
- `src/application/workflows/ingestion/pipeline/stage_lifecycle/ingestion_stage_sequence_executor.py` (add structured logging)
- `src/domain/workflow/ingestion_run.py` (already has `error_message: str | None` — add `warnings: list[str] = field(default_factory=list)` alongside it, following the same pattern as `parser_name`/`parser_version` which are already structured fields here)
- `src/infrastructure/db/mappers/workflow/` (find the `IngestionRun` mapper and persist the new column — check for an existing migration pattern under `alembic`/`migrations`)
- `src/application/workflows/ingestion/pipeline/stage_lifecycle/stage_state_applier.py` (or wherever `apply_parsing` lives — set `ingestion_run.warnings` the same place `parser_name`/`parser_version` are already stamped)

**Fix**: this is the one item in this plan that touches persistence (new column + migration), because `IngestionRun` is already the natural home — it already carries `parser_name`/`parser_version` per-run, so `warnings` belongs right next to them rather than as a new concept:

```python
# src/domain/workflow/ingestion_run.py
@dataclass(slots=True)
class IngestionRun:
    ...
    parser_name: str | None = None
    parser_version: str | None = None
    warnings: list[str] = field(default_factory=list)  # new
```

Plus a minimal structured log line at the point warnings are already collected, so even before the DB column ships, warnings are grep-able in production logs:

```python
# ingestion_stage_sequence_executor.py, in _run_parsing, after warnings.extend(...)
if parsing_result.parse_warnings:
    logger.warning(
        "parsing produced warnings",
        extra={
            "document_id": parsing_result.document_graph.document.document_id,
            "correlation_id": correlation_id,
            "warnings": parsing_result.parse_warnings,
        },
    )
```

(Check whether this module already has a module-level `logger = logging.getLogger(__name__)` — none was found in the files read for this audit, so one will need adding.)

### 2.3 Parsing never writes an audit record

**Problem**: `ParsingWorkflow.parse()` is decorated `@tracked_action(action="parsing.workflow_completed", activity=True, audit=False, event=False)` (`parsing_workflow.py:57-63`) — audit explicitly off, while `IngestionWorkflow`, `DeleteDocumentWorkflow`, `DocumentRegistrationService`, `ClassificationService`, and `ExtractionService` all set `audit=True`.

**Why it matters**: inconsistent audit coverage for engineering/compliance-relevant documents is a governance gap that's easy to fix and easy to forget.

**Affected files**:
- `src/application/workflows/parsing/parsing_workflow.py` (one-line flag flip)

**Fix**: confirmed safe by reading `tracked_action`'s implementation (`src/shared/execution/tracked_action.py:48-55`) — `audit=True` just adds a call to `AuditTracker.record_success`/`record_failure` using the same `self`/`action`/context already resolved for the activity tracker. No new parameters, no signature change:

```python
@tracked_action(
    action="parsing.workflow_completed",
    entity_type="document",
    activity=True,
    audit=True,   # was False
    event=False,
)
def parse(self, ...):
```

### 2.4 Idempotency is parser-version-blind

**Problem**: `IngestionDuplicateCoordinator.check_content_hash_duplicate()` (`ingestion_duplicate_coordinator.py:89-124`) short-circuits on content-hash match alone via `duplicate_check_step.check_content_hash_duplicate`. `IngestionRun` already has structured `parser_name`/`parser_version` fields (`ingestion_run.py:23-24`) populated per run — but nothing compares the stored value against the *current* `DoclingParser.parser_version` before deciding to skip.

**Why it matters**: after a Docling upgrade, re-ingesting an unchanged file is indistinguishable from re-ingesting a genuine duplicate — it gets skipped, silently perpetuating a stale, possibly lower-quality parse. This is a common enterprise pain point: "we upgraded the parser six months ago, which of our 10,000 documents still need reprocessing?" is currently unanswerable without a full manual audit.

**Affected files**:
- `src/application/services/document/duplicate_detection_service.py` (fetch stored parser_version alongside the existing content-hash lookup)
- `src/infrastructure/db/repositories/document/document_duplicate_checker.py` (extend the query — needs the document's `parser_version` to be queryable; currently it's inside the document's opaque `metadata_json` blob per `document_mapper.py`, not a first-class column)
- `src/application/contracts/document/document_repository.py` (interface signature, if the lookup method's return shape changes)
- `src/application/workflows/ingestion/pipeline/duplicate_handling/duplicate_check_step.py` (decision logic: only short-circuit when hash *and* parser version match)
- A DB migration adding a structured `parser_version` column to the document table (needed regardless — see 4.2), so this dedup query doesn't have to parse JSON on every check

**Fix approach** (needs the schema change from 4.2 landed first, hence listed here as the consuming logic):

```python
# duplicate_check_step.py — sketch, exact signature depends on document_repository's interface
def check_content_hash_duplicate(self, *, request, content_hash, activity_context):
    existing = self.document_repository.find_by_content_hash(content_hash)
    if existing is None:
        return None
    if existing.parser_version != self.current_parser_version:
        return None  # stale parse — treat as "not a duplicate", let it reprocess
    return existing.document_id
```

This changes ingestion semantics (a same-content re-ingest after a parser upgrade now reprocesses and presumably creates/replaces a document graph rather than skipping) — confirm with the team whether reprocessing should *replace* the existing document or version it, since that decision belongs to `DuplicateIngestionExitHandler`/`DocumentRegistrationService`, not this check alone. Flagging as a design decision, not just an implementation detail.

### 2.5 No retry on OCR failures

**Problem**: `OCRService.extract_result_from_image()` (`src/application/services/ai/ocr_service.py:32-47`) calls the `OCRProvider` directly with no retry wrapper. `PageOCRFallbackWorkflow` catches failures per-target (good, see prior audit note) but never retries before recording the failure.

**Why it matters**: transient resource contention (the local OCR engine under memory/CPU pressure from concurrent ingestion) currently produces a permanent per-page OCR gap instead of a retried success.

**Affected files**:
- `src/application/services/ai/ocr_service.py`
- `src/config/settings/` (new `ocr_retry_attempts` setting, small default like 2)

**Fix**: a small manual retry loop is enough here — no new dependency needed for 1-2 retries with a short fixed backoff:

```python
# ocr_service.py
def extract_result_from_image(self, image_path: str) -> OCRResult:
    last_exc: Exception | None = None
    for attempt in range(1 + self.retry_attempts):
        try:
            return self._extract_once(image_path)
        except (InfrastructureError, OCRProviderError) as exc:
            last_exc = exc
            if attempt < self.retry_attempts:
                time.sleep(self.retry_backoff_seconds * (attempt + 1))
    raise last_exc
```

---

## Phase 3 — Extraction fidelity for shipyard-style technical documents

### 3.1 Cross-reference detection misses Table/Figure/Drawing references

**Problem**: `ChunkCrossReferenceDetector` (`builders/document_graph/chunk_cross_reference_detector.py:15-39`) only has `_PAGE_REFERENCE_PATTERNS` and `_SECTION_REFERENCE_PATTERNS` (lines 15-38). No pattern for "Table N", "Figure N", or drawing identifiers like "Drawing SK-1044" — exactly the reference style dense in engineering manuals.

**Why it matters**: these references currently flatten to plain text with no structured link, so a retrieval answer citing "see Table 3" can't actually surface Table 3.

**Affected files**:
- `src/application/workflows/parsing/builders/document_graph/chunk_cross_reference_detector.py` (new pattern list)
- A new resolver, e.g. `chunk_asset_reference_resolver.py`, alongside the existing `ChunkCrossReferenceResolver`/`ChunkSectionReferenceResolver` — table/figure references resolve to a `TableAsset`/`PictureAsset` id, not a chunk, so this needs its own resolution target rather than reusing the page/section resolvers as-is.
- `builders/document_graph/chunk_cross_reference_linker.py` (wire the new resolver into the existing linking pass)
- Domain: check `src/domain/document/entities/chunk.py` for where `ChunkCrossReference` rows attach — a table/figure reference likely needs a `target_type` discriminator (`chunk` vs `table_asset` vs `picture_asset`) if one doesn't already exist.

**Fix** (detection half — the safer, additive part to land first):

```python
# chunk_cross_reference_detector.py
_ASSET_REFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsee\s+table\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\btable\s*(\d+(?:\.\d+)*)\s+(?:above|below)\b", re.IGNORECASE),
    re.compile(r"\bsee\s+figure\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\bfig\.\s*(\d+(?:\.\d+)*)\b", re.IGNORECASE),
    re.compile(r"\bdrawing\s+([A-Z]{1,4}-\d+[A-Z]?)\b", re.IGNORECASE),
)
```

Drawing-ID formats vary a lot between shipyards — treat the pattern above as a starting point and get real sample documents from the teams before finalizing the regex; don't guess a shipyard-specific numbering scheme from first principles.

### 3.2 Numbered procedure steps can split across chunk boundaries

**Problem**: `ChunkFragmentPacker.pack()` (`builders/chunking/builders/section_chunk/chunk_fragment_packer.py:38-129`) treats every non-standalone fragment (including each `LIST_ITEM`) independently — it only flushes on token budget or `SectionMergePolicy.should_flush_on_section_change()`. There is no rule keeping a numbered sequence of steps together.

**Why it matters**: a 20-step maintenance procedure can fracture mid-sequence with only a 20-100 token overlap tail carrying context forward. For a shipyard maintenance-procedure RAG use case, a retrieved chunk containing steps 7-11 without the sequence's setup/safety-warning context is a correctness and safety-adjacent risk, not just a quality nit.

**Affected files**:
- `src/application/workflows/parsing/builders/chunking/models/chunk_fragment.py` (needs a way to mark "part of an ordered list run" — likely a `list_sequence_id`/`list_position` field, populated wherever fragments are built from `LIST_ITEM` elements)
- `src/application/workflows/parsing/builders/chunking/builders/fragment/chunk_fragment_builder.py` (populate the new field when building fragments)
- `src/application/workflows/parsing/builders/chunking/policies/section_merge_policy.py` (the natural home for a new `should_flush_mid_list()` rule, alongside the existing `should_flush_on_section_change()`)
- `src/application/workflows/parsing/builders/chunking/builders/section_chunk/chunk_fragment_packer.py` (consult the new policy before flushing)
- `src/config/chunking/*.yaml` (expose as a per-profile toggle — a `DATASHEET` profile may not care, `MANUAL` should)

**Fix approach** — this needs new state on `ChunkFragment` before the packer logic changes, so treat it as two PRs:
1. Tag consecutive `LIST_ITEM` fragments from the same list with a shared `list_run_id` in the fragment builder (a monotonic counter reset whenever the underlying element stream leaves a list context).
2. Add a policy check in the packer's flush decision: don't flush *inside* a `list_run_id` purely for section-boundary reasons, and prefer to flush *before* a list run starts rather than mid-run when a token-budget split is unavoidable — a full list exceeding `max_chunk_tokens` is an explicit, documented exception (log it, don't silently truncate), not a case worth complex handling in v1.

Do not attempt to guarantee "a list never splits" unconditionally — a single list can legitimately exceed the configured chunk size. The goal is "don't split a list for a reason other than exceeding max_chunk_tokens," which is a much smaller, achievable change.

### 3.3 OCR/table-detection thresholds aren't configurable per document type

**Problem**: Docling-level settings (OCR engine, table-structure mode, `bitmap_area_threshold`, etc.) live in one global `DoclingSettings` (`src/config/settings/docling_settings.py`), env-var-driven, process-wide. Contrast with chunking, which already has a clean per-profile YAML mechanism (`ChunkingPolicyRegistry`, `src/config/chunking/*.yaml`).

**Why it matters**: a `DRAWING`-profile document (mostly diagrams, little running text) plausibly needs different OCR/table thresholds than a `MANUAL`. Today that's impossible without a process-wide env var change affecting every team's documents.

**Affected files**:
- `src/config/settings/docling_settings.py`
- `src/infrastructure/parsing/docling/docling_converter_factory.py` (accept an override bundle, mirroring how `enable_ocr_override` already threads through)
- New `src/config/parsing/*.yaml` profile files, mirroring `src/config/chunking/*.yaml`'s structure/loader pattern

**Fix**: this is a larger, lower-urgency item — recommend deferring until 3.1/3.2 land and treating it as "extend the existing `ChunkingProfile`-per-document-type mechanism to cover Docling knobs," reusing the same YAML-loading code path (`ChunkingPolicyRegistry`) rather than inventing a second config system. Not sketched in code here because it should follow whatever the chunking registry's loader interface looks like exactly, to avoid two divergent per-profile config mechanisms in the same codebase.

---

## Phase 4 — Cleanup (low urgency, low risk)

### 4.1 Remove dead code in `LayoutHeuristicStrategy`
`builders/section_hierarchy/layout_heuristic_strategy.py:66-67` has an `if ...: pass` block with no effect. Confirm it's genuinely vestigial (not a placeholder for an intended branch someone forgot to fill in) before deleting — if it's the latter, that's actually a Phase 3 correctness bug, not cleanup.

### 4.2 Structured `parser_version` column on the document table
`document_mapper.py` currently serializes `document.metadata` (including `parser.version`) as an opaque JSON blob (`metadata_json`). Add a first-class, indexed `parser_version` column populated from `DocumentPersistentMetadataBuilder` at write time. This is a prerequisite for 2.4 (version-aware idempotency) and also answers "which documents need reprocessing after a Docling upgrade" with a simple query instead of scanning JSON.

**Affected files**: the document table migration, `src/infrastructure/db/mappers/document/document_mapper.py`, `src/application/workflows/parsing/builders/document_graph/document_persistent_metadata_builder.py`.

### 4.3 Export `stage_durations` to production telemetry
`ParsingPerformanceGate` (`src/application/evaluation/parsing/parsing_performance_gate.py`) already knows how to evaluate `stage_durations` against thresholds, but only runs offline via `scripts/run_parsing_performance_gate.py`. Once 2.2's logging lands, emit `stage_durations` as structured log fields (or metrics if there's a metrics client elsewhere in the codebase — none was found in this audit, so check before introducing one) at the same point, so parsing performance regressions are visible without a manual script run.

---

## Sequencing summary

| Phase | Theme | Landing order reason |
|---|---|---|
| 1 | Availability & input safety | Everything else assumes a document either finishes parsing or fails cleanly and in isolation — Phase 1 makes that true |
| 2 | Data quality & governance | Wires existing computed signals (`parse_confidence`, `parse_warnings`, `parser_version`) through instead of discarding them; 2.4 needs 4.2's schema change |
| 3 | Extraction fidelity | Independent of 1-2; can run in parallel by a different engineer/team once Phase 1 is stable |
| 4 | Cleanup | No dependencies, pick up opportunistically |

Suggested effort shape (not a commitment — size against your own team's velocity): Phase 1 is a few days of focused work per item, all independently shippable. Phase 2 is similar except 2.4, which is a schema change plus a semantics decision that needs product sign-off. Phase 3 is the largest single item (3.2 in particular needs sample shipyard documents to validate against, not just unit tests) and can run concurrently with Phase 1/2 by a different owner.
