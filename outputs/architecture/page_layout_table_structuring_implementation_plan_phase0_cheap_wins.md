# Concrete Implementation Plan: Phase 0 — Cheap, Low-Risk Fixes

Part of the concrete implementation plan set — see
`page_layout_table_structuring_implementation_plan_index.md`. Three independent, small fixes.

## 0.1 `ChunkClassificationWorkflow` — remove it (dead code, confirmed)

Verified: it runs a full LLM call per chunk (gated by `chunk_classification_enabled`, distinct
from the live `chunk_type_classification_enabled` flag that gates the useful
`ChunkTypeClassificationWorkflow`) and persists to `ChunkClassificationORM`. Grep across all of
`src/` confirms **zero callers** of `get_chunk_classification`/`list_chunk_classifications` outside
their own definitions — nothing in retrieval or QA ever reads it back.

**Recommendation: delete it outright** (not just disable) — it's pure write-only overhead with no
consumer and no other phase in this plan depends on it.

Ordered deletions/edits:
1. `src/application/orchestrator/ingestion/ingestion_orchestrator.py` — remove
   `ChunkClassificationWorkflow` construction and the kwarg passed into
   `PostClassificationChunkFinalizationWorkflow(...)`.
2. `post_classification_chunk_finalization_workflow.py` — remove the
   `chunk_classification_workflow` param and the call to
   `classify_chunks_if_enabled(...)`. Keep `classify_chunk_types_if_enabled(...)` (unaffected,
   different feature).
3. `final_chunk_classification_runner.py` — delete `classify_chunks_if_enabled` and its
   constructor params; keep the class for the type-classification method only.
4. Delete `chunk_classification_workflow.py` entirely.
5. `classification_settings.py` — delete `chunk_classification_enabled` and
   `chunk_confidence_threshold` (re-grep `chunk_confidence_threshold` for other readers first).
   **Do not delete `chunk_classification_llm`** — it's also read as a fallback by the live
   `ChunkTypeClassificationWorkflow`.
6. `classification_workflow_settings.py` — delete `default_enable_chunk_classification()`.
7. `ClassificationService` / `ClassificationRepository` (contract + SQLAlchemy impl) — delete
   the four chunk-classification methods (`save_chunk_classification(s)`,
   `get_chunk_classification`, `list_chunk_classifications`).
8. Delete `chunk_classification_reader.py`, `chunk_classification_writer.py`,
   `chunk_classification_mapper.py` (and their `__init__.py` exports).
9. Delete `ChunkClassificationORM` from `classification_models.py` (+ export).
10. Delete the `ChunkClassification` domain dataclass (**not** `ClassificationResult`, which is
    shared with `DocumentClassification` and stays).
11. Delete `ChunkClassificationValidator` only if nothing else constructs a `ChunkClassification`
    to validate (re-grep first).
12. Optional: add an Alembic migration dropping the `chunk_classifications` table for a clean
    prod story (runtime schema creation is additive-only via `create_all`, so this isn't
    functionally required for existing DBs, just cleanliness).
13. Delete/trim: `test_chunk_classification_workflow.py` and the
    `chunk_classification_workflow`-related fixtures inside the finalization-workflow test parts;
    grep `tests/` for the deleted classes and trim accordingly.

**Alternative (if the team wants to keep it as an audit trail instead):** keep every file, add a
new `ChunkClassificationConsistencyChecker.check()` collaborator called right before
`save_chunk_classifications`, comparing `classification.chunk_type` against `chunk.chunk_type` and
only `logger.warning(...)` on mismatch (never raising, never mutating `chunk.chunk_type`). Gate
behind a **new**, separately-defaulted-OFF flag
(`chunk_classification_consistency_check_enabled`) so turning on the already-off legacy workflow
doesn't silently start emitting new warnings without a second explicit opt-in. New test:
`test_chunk_classification_consistency_checker.py`. Deletion (above) is still the recommended
default; this is documented as the fallback if the team wants to preserve the data path.

## 0.2 Hardcoded English-only `"Page"` literal in TOC reconstruction

Exact gate: `docling_parallel_toc_reconstructor.py::_looks_like_reconstructed_toc()` returns
`header[-1] == "Page"` — a literal string match against a header label a *different* file
(`docling_toc_table_row_reconstructor.py`) happens to invent. The reconstructor's own logic never
actually depends on English words (it already extracts page numbers via a digit regex,
`_extract_row_page`, `re.fullmatch(r"\d{1,4}", cells[index])`) — only the acceptance *gate* is
coupled to the literal text.

**Fix:** promote the existing digit regex to a shared, importable pattern instead of a second copy:
1. In `docling_toc_table_row_reconstructor.py`, add module-level
   `TOC_PAGE_NUMBER_PATTERN = re.compile(r"\d{1,4}")`; use it in `_extract_row_page` (behavior
   identical, just named/exported).
2. In `docling_parallel_toc_reconstructor.py`, import `TOC_PAGE_NUMBER_PATTERN` and rewrite
   `_looks_like_reconstructed_toc` to check that every reconstructed data row's **last cell** is a
   1-4 digit page number, instead of checking the header text:
   ```python
   data_rows = reconstructed[1:]
   return bool(data_rows) and all(
       bool(row) and TOC_PAGE_NUMBER_PATTERN.fullmatch(str(row[-1]).strip())
       for row in data_rows
   )
   ```
   This is language-agnostic: it makes no assumption about header or title text language.
3. **Behavior preservation**: the header text itself is unchanged, so every existing test
   asserting on `["Number", "Title", "Page"]` keeps passing unmodified — this is a pure
   detection-mechanism change.

**New tests** (neither class has a dedicated test file today):
- `test_docling_toc_table_row_reconstructor.py` — English baseline + a **non-English fixture**
  (e.g. French TOC rows with accented titles) proving reconstruction never depended on English
  words, only digit patterns.
- `tests/.../table_layout/test_docling_parallel_toc_reconstructor.py` (new subdirectory) — two-lane
  merge with non-English titles, plus an explicit regression test: a stub reconstructor returning
  a header whose last column is a *localized* word (e.g. `"Página"`) but whose data rows still end
  in digits — assert detection still succeeds.

## 0.3 File-size drift: split two files back under 300 LOC

Both files were previously documented elsewhere in this repo as required to stay ≤300 LOC and
have since regrown past it.

**`docling_document_normalizer.py` (332 LOC).** The repo's own refactor plan already specified
this exact split when the file was 262 LOC and exempt — execute it now:
1. New `docling_value_accessors.py` — bare functions `get_value()`/`clean_text()` (moved from
   `_get_value`/`_clean_text`, unchanged bodies).
2. New `docling_element_text_resolver.py` — class `DoclingElementTextResolver` (constructor takes
   `table_extractor`), with `extract_text`, `extract_table_markdown`, `extract_caption_text`,
   `extract_table_structure`, `extract_section_title` moved from their `_extract_*` counterparts.
3. New `docling_element_metadata_builder.py` — class `DoclingElementMetadataBuilder` (constructor
   takes `item_extractor`, `table_extractor`), with `build()` moved from `_build_metadata`.
4. Slim `docling_document_normalizer.py` to `__init__` + `normalize()`, delegating to
   `self.text_resolver`/`self.metadata_builder` (both optional constructor params, default to a
   new instance — matches this package's existing collaborator-injection convention). Estimated
   result: ~95-110 LOC.
5. No changes needed to existing tests (all go through the public `normalize()` API). **New**
   tests required for the three new modules: `test_docling_value_accessors.py`,
   `test_docling_element_text_resolver.py`, `test_docling_element_metadata_builder.py`.

**`document_graph_reader.py` (322 LOC).** This file was *already split once* (prior refactor:
`document_reader.py` → `document_reader.py` + `document_graph_reader.py` at ~190 LOC) and has
regrown +132 lines (+70%) since, almost entirely inside `_rehydrate_assets` and its private
cleaning helpers (~192 of 322 lines) — the part of the file that keeps absorbing new
table-classification metadata fields as table-shape/category coverage grows (exactly what Phase 3
of this plan is about to add more of). Split so that growth center is isolated this time:
1. New `document_graph_value_cleaners.py` — bare functions: `clean_text`, `clean_multiline_text`,
   `clean_rows`, `clean_parallel_stream_rows`, `coerce_float`, `clean_header_paths`,
   `clean_axis_summary` (moved from the file's private static/classmethods, unchanged bodies).
2. New `document_graph_asset_rehydrator.py` — one function, `rehydrate_assets(graph:
   DocumentGraph) -> None` (moved from `_rehydrate_assets`, calling the new cleaner functions
   directly rather than `self._clean_*`).
3. Slim `document_graph_reader.py` to `__init__`, `get_document_graph()` (now calling
   `rehydrate_assets(graph)` directly), and `_group_element_ids_by_section()`. Estimated result:
   ~110-130 LOC — deliberately more headroom than the prior split's ~190-line budget, specifically
   because the identified growth center is now isolated in its own file.
4. Test moves: move all 5 existing `_rehydrate_assets` tests from `test_document_graph_reader.py`
   to a new `test_document_graph_asset_rehydrator.py` (update call sites to the new function
   import; assertions unchanged). Add a new small test to the now-slimmed
   `test_document_graph_reader.py` covering `_group_element_ids_by_section` directly (previously
   only indirectly covered). Add a new `test_document_graph_value_cleaners.py` with direct
   `None`/malformed-input coverage for each of the 7 extracted functions.

Both splits are pure structural moves with unchanged bodies — no behavior change, no flag needed.
