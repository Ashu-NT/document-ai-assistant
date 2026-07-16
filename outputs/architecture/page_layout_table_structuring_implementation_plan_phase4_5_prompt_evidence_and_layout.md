# Concrete Implementation Plan: Phase 4/5 — Prompt Evidence & Layout Propagation

Part of the concrete implementation plan set — see
`page_layout_table_structuring_implementation_plan_index.md`.

## Phase 4: Make structured table evidence first-class at the prompt boundary

**Verified current state**: `_source_payload()` omits `table_rows` even though it's already
populated end-to-end on both `AnswerSource.table_rows` and `PromptSourceView.table_rows`. The
separate top-level `"tables"` array is **not** a redundant duplicate — it's load-bearing: built by
`PromptTableProjector` with normalized headers/`cells_by_header`/`table_type`/a stable `table_id`,
and consumed by `PromptEvidenceTopologyBuilder` for `source_families`/`section_topology`. And
`source.content` already contains a markdown rendering of the table for table-typed chunks. So the
gap isn't "the LLM sees nothing" — it's "no machine-exact, unambiguous cell grid directly on the
source record" (markdown parsing is lossy for cells containing `|`, wrapped text, merged cells).
An existing test hard-asserts today's omission
(`test_serializer_preserves_nested_entity_relationships_and_first_class_tables` asserts
`'"table_rows": [' not in payload`) — this is a real behavior contract, must stay true by default.

**Decision: keep the `"tables"` array (do not merge/remove it), add `table_rows` to
`_source_payload()` gated behind a new settings flag defaulting `False`.**

Steps:
1. New `src/config/settings/prompt_context_settings.py` — `PromptContextSettings` with
   `max_items_per_array: int = 20`, `include_source_table_rows: bool = False`
   (`PROMPT_CONTEXT_INCLUDE_SOURCE_TABLE_ROWS`), `max_table_rows_per_source: int = 20` (a
   **separate** cap from `max_items_per_array` — one bounds list-of-things count, the other bounds
   rows-within-one-table, an orthogonal budget). Register in `settings.py`/`__init__.py` exactly
   like `docling_settings` (direct module-level singleton import/consumption — confirmed as this
   repo's established pattern, not constructor injection).
2. Delete the bare `_MAX_ITEMS_PER_ARRAY = 20` constant; `_capped()` reads
   `prompt_context_settings.max_items_per_array` when no explicit `limit` is passed (all existing
   call sites keep working unchanged).
3. `_source_payload()`: after building the existing dict, conditionally add
   `payload["table_rows"] = self._capped(source.table_rows, limit=prompt_context_settings.max_table_rows_per_source)`
   only when `include_source_table_rows` is `True` and `source.table_rows` is truthy — so the key
   is entirely absent (not `null`) by default, preserving the exact existing test assertion.
4. Optional: append a clause to `evidence_schema_formatter.py`'s `"sources"` bullet, conditional on
   the same flag, so the schema description stays truthful either way.

Tests: keep the existing default-off assertion; add a flag-on test asserting `table_rows` appears
and matches the decoded fixture; add a cap test proving truncation to `max_table_rows_per_source`.
New `tests/unit/config/settings/test_prompt_context_settings.py` (no settings module has a test
today — first of its kind, verifying defaults and env-alias overrides).

## Phase 5a: Typed layout fields on `TableAsset`

**Before implementing this sub-phase, read
`page_layout_table_structuring_implementation_plan_migration_and_compatibility.md` in full** — it
covers, with code-verified specifics: why no DB migration is needed here, the exact rehydration
safe-default contract to follow, a real single-source-of-truth bypass found in
`LogicalTableFamilyResolver` that needs a decision during implementation, a concrete backfill
script design for already-ingested documents, and multi-page/continuation-table behavior
(confirmed already-safe, with one new regression test to add).

The exact field names asked for already exist verbatim in the serialized per-element metadata
(`LayoutMetadataSerializer.serialize()` produces `layout_region_id`, `layout_region_role`,
`layout_lane_count`, `layout_reading_order`, `layout_model_version`, plus conditional
`layout_is_front_matter`, `layout_lane_index`, `layout_region_bbox`, `page_orientation`) — this is
a pure "read what's already being persisted" change, no new upstream plumbing needed.

Add to `TableAsset` (all new, `None`-default, appended after existing fields):
```python
layout_region_id: str | None = None
layout_region_role: str | None = None
layout_lane_index: int | None = None
layout_lane_count: int | None = None
page_orientation: str | None = None
```
**Safety confirmed**: every `TableAsset(...)` call site across production/tests/scripts uses
keyword arguments exclusively (no positional or exhaustive-schema construction) — additive fields
are safe with zero flag needed, consistent with how `table_shape`/`table_structure_quality` were
added previously.

Populate at both construction points: `ParsedAssetFactory.build_table_asset()` (read from
`parsed_element.metadata`, add a new `_coerce_int` helper mirroring the existing `_coerce_float`)
and `DocumentGraphReader`'s rehydration (read from `parser_extra`, same helper mirrored there). No
ORM/mapper changes needed — `parser_extra` is already a generic JSON blob already carrying these
keys; this only adds code that *reads* them.

Tests: extend `test_table_asset.py` (fields settable + default to `None`),
`test_parsed_asset_factory.py` (metadata → `TableAsset` round-trip including int coercion and
absent-key → `None`), `test_document_graph_reader.py` (same round-trip via
`get_document_graph()`).

## Phase 5b: Lane-detection — do NOT merge; add a cross-check log only

Comparison: `LayoutLaneDetector` operates on whole-page elements with fixed boundary ratios, to
decide 1-vs-2-column page layout. `ParallelTableStreamClusterer` operates on one table's individual
cells with an adaptive gap-threshold, to split a merged cell grid into N side-by-side sub-tables.
Different input granularity, different problem, different threshold philosophy.

**Recommendation: do not merge.** Forcing a lowest-common-denominator abstraction over two
different heuristic regimes adds coupling risk to an already fragile, empirically-tuned area for
speculative benefit — explicitly the highest-risk item in this whole plan set. Instead, thread the
already-computed page-level lane count through as an **optional** cross-check input, used only to
`log.info` a disagreement — zero change to returned rows:

1. `ParallelTableStreamClusterer.cluster(spans, *, page_lane_count: int | None = None)` — if
   provided and `len(result) != page_lane_count`, log an INFO-level disagreement; never alters the
   return value.
2. Thread `page_lane_count: int | None = None` (keyword-only, default `None`, fully backward
   compatible) straight through `DoclingParallelTableReconstructor.reconstruct()` →
   `DoclingTableRowGridBuilder.build_reconstruction()` → `DoclingTableExtractor.extract_structure()`.
3. In `docling_document_normalizer.py`, the per-element `layout_lane_count` is already computed
   up-front in `layout_metadata_by_element_ref` before the per-item loop — look it up for the
   current table item and pass it into `extract_structure(item, page_lane_count=...)`.
4. Keep this strictly additive — no branch may alter `rows`/`parallel_stream_rows` based on the
   new parameter; risk is bounded to "a new log line might fire," nothing else, despite touching
   five method signatures across the call chain.

Tests: new `test_parallel_table_stream_clusterer.py` and
`test_docling_parallel_table_reconstructor.py` (neither exists today) proving the parameter is a
pure pass-through (identical clusters/result with or without it) plus the log-message assertion
via `caplog`; extend the grid-builder/table-extractor/document-normalizer tests for the new
optional-parameter threading.

## Phase 5c: Front-matter detector unification

`FrontMatterPageClassifier` (page-density: numbered headings, body-text volume) and
`SectionChunkSkipper._is_front_matter_section` (section/title/page-number heuristic) are
complementary signals, not redundant — keep both, thread the parsing-time signal in as an
*additional* input to the chunking-time decision, not a replacement.

1. `parser_metadata.extra` already carries `layout_is_front_matter` for elements on a classified
   front-matter page (same JSON blob used in Phase 5a) — confirmed reachable at
   `SectionChunkSkipper.should_skip_section()`'s existing `elements: list[CanonicalElement]` param.
2. Add `_has_layout_front_matter_signal(elements) -> bool` helper checking that key across the
   section's elements.
3. **Gate behind a new flag** (`chunking_settings.use_layout_front_matter_signal`, default
   `False`) rather than an unconditional additive `if ...: return True` — this is a strict
   "more aggressive front-matter skip" behavior change for existing corpora, so per the standing
   "preserve current behavior unless config overrides" rule it must default OFF. When enabled,
   insert the check after the existing structural guards (`parent_section_id is not None`/
   `page_end > 2`) and before the token-heuristic logic, so it can only add `True` results within
   the same early-document-only scope the method already assumes.

Tests: extend `test_section_chunk_skipper.py` with elements carrying `layout_is_front_matter`,
asserting `should_skip_section()` returns `True` only when the flag is on, and that flag-off
behavior is byte-identical even with the signal present.

## Sequencing note

5a has no dependency on 5b/5c and is the safest, lowest-risk of the three (purely additive fields).
5b is the highest-risk item in the entire plan set — schedule it last within this phase, and only
after 5a's typed fields give a clean way to inspect layout data once wired downstream. 5c can run
independently of both.
