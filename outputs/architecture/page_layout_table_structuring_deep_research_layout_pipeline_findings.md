# Deep Research: Page Layout and Table Reconstruction Pipeline

Part of the deep research set — see `page_layout_table_structuring_deep_research_index.md` for
scope. This file covers the subsystem added by commit `66ca6f0` ("pagelayoutInferer",
2026-07-15) and its own 1,199-line plan document,
`outputs/architecture/layout_aware_page_region_and_table_reconstruction_plan.md`.

## A. Plan vs. implementation gap

The plan's core architectural decision was explicit: *"Introduce a dedicated page-layout analysis
layer inside parsing, then make TOC reconstruction and table reconstruction consume that layout
model before semantic classification and logical-family resolution."*

**That decision was not implemented.** A clean, well-decomposed `layout/` package was built
(`page_orientation_resolver.py`, `layout_lane_detector.py`, `layout_region_builder.py`,
`front_matter_page_classifier.py`, `layout_reading_order_resolver.py`, `page_layout_analyzer.py`,
`layout_metadata_serializer.py`) computing orientation, lanes, regions, reading order, and
front-matter status. But table/TOC reconstruction does **not** consume it. Instead, a second,
fully independent lane-detection mechanism was built inside
`normalizers/table_layout/parallel_table_stream_clusterer.py`, re-deriving lanes from raw
`TableCellSpan` bboxes with its own gap-threshold heuristic
(`gap_threshold = max(page_width*0.12, median_width*1.6, 36.0)`), unrelated to
`LayoutLaneDetector`'s fixed boundary ratios (`_LEFT_BOUNDARY_RATIO=0.56`,
`_RIGHT_BOUNDARY_RATIO=0.44`). `DoclingParallelTableReconstructor.reconstruct()` never receives a
`PageLayoutRegion`/`PageLayoutAnalysis` object at all — only raw cell spans. The plan's proposed
`tables/reconstruction/` package was never created; the real package lives at a different path
and reimplements lane detection from scratch.

Phase-by-phase status against the plan's own self-graded progress section:

- **Phase 1 (layout foundation): done**, matches the plan's proposed structure closely.
- **Phase 2 (region-aware TOC): partially true, but disconnected.** `DoclingParallelTocReconstructor`
  does reconstruct dual-column TOCs from cell geometry, but the plan's stated acceptance
  criterion — preventing TOC tables from inheriting front-matter/copyright section ownership —
  is not wired through. The new `FrontMatterPageClassifier` signal is consumed only inside the
  `layout/` package itself; a second, older, unrelated front-matter heuristic
  (`section_chunk_skipper.py`, page-number/title based) is what actually governs chunk/section-path
  skipping, and the two mechanisms never reference each other.
- **Phase 3 (region-aware table reconstruction): "partial" is fair**, but it operates on
  table-cell-local geometry only, not the page-level `PageLayoutRegion` model — "region-aware"
  here means table-interior lane clustering, not the page-level abstraction the plan called for.
- **Phase 4 (logical family resolver upgrade): done and tested.**
  `LogicalTableFamilyResolver._same_page_regions_are_compatible()` reads `layout_region_id`,
  `layout_lane_count`, `layout_lane_index` and rejects same-page continuation across incompatible
  lanes — the one place page-layout metadata genuinely drives a downstream decision, with a
  dedicated regression test.
- **Phase 5 (semantic/chunking alignment): narrow slice only.** `TableRowSemanticNormalizer` now
  also normalizes `parallel_stream_rows`, but its specialized-normalizer delegation list is
  unchanged — still only spare-parts and troubleshooting (see the structuring findings file).
- **Phase 6 (debug/persistence surfaces): not implemented.** `scripts/debug_parse_document.py`
  and `scripts/export_document_table_assets.py` are untouched by this commit despite being named
  as required verification surfaces in the plan itself.
- **Phase 7 (QA/prompt propagation): not implemented** — see section B below.

**Rule violation:** the plan states no touched file may exceed 300 LOC. Two files touched by
this commit now do: `docling_document_normalizer.py` at 332 LOC, `document_graph_reader.py` at
322 LOC. `logical_table_family_resolver.py` sits at exactly 300, with zero headroom.

**Guardrail violation:** the plan's own central rule is that lexical/marker-driven logic must
stay "low-to-medium confidence, never primary," specifically to avoid overfitting to the current
document set. `docling_toc_table_row_reconstructor.py` hardcodes the TOC header as literal
English strings (`["Number", "Title", "Page"]` / `["Title", "Page"]`), and
`docling_parallel_toc_reconstructor.py`'s `_looks_like_reconstructed_toc` gates the entire
parallel-TOC-stream acceptance decision on `header[-1] == "Page"` — a hardcoded, English-only
literal baked into the reconstruction pipeline itself, contradicting the same document's stated
design principle.

## B. Layout metadata propagation verdict

Baseline Finding #6 ("layout region/lane/orientation metadata is not carried downstream as
first-class prompt evidence") is **partially fixed** — fixed at the parsing/family-resolution
layer, still true at retrieval/prompt/answer-context layers.

Evidence: a repo-wide search for the layout field names (`layout_region_id`,
`layout_region_role`, `layout_lane_index`, `layout_lane_count`, `layout_region_bbox`,
`layout_reading_order`, `page_orientation`, `layout_is_front_matter`) returns hits only inside
`parsing/layout/` and `logical_table_family_resolver.py` — zero hits in
`infrastructure/db/mappers/`, `question_answering/`, `prompts/`, or `answer_generation/`.
`TableAsset` itself has no fields for region id/role/lane/orientation/bbox at all — only a
table-internal `local_reading_order` string, a different concept. `DocumentGraphReader`'s
rehydration method reads dozens of `parser_extra` keys but never reads any of the layout fields,
so they round-trip as an inert JSON blob and never become a typed object anywhere past parsing.

The one genuine consumption is the family-merge guardrail in section A (Phase 4) — a parsing-time
decision only, not inspectable evidence later. Partial mitigation exists through a different
channel: `parallel_stream_rows` *content* (not the layout metadata itself) does reach QA as
prose, via `TableAsset.to_structured_row_text()` and `TableStructureContextRenderer`, which do
inject "Parallel streams: N (...)" text into hydrated evidence. So table-level stream separation
quality reaches the model; page-level layout semantics (region, role, orientation, front-matter
status) do not.

## C. Test coverage gaps

The entire `table_layout/` reconstruction package (7 files: parallel table/TOC reconstructors,
cell candidate builder, quality evaluator, stream clusterer, reconstruction result) has **zero
dedicated test files** — all coverage is incidental, via a grid-builder test that only exercises
the successful-reconstruction path, never rejection/fallback/edge-case branches.

Within the `layout/` package (8 files), only `page_layout_analyzer.py` has a direct test (2
scenarios); the other seven — `front_matter_page_classifier.py`, `layout_lane_detector.py`,
`layout_metadata_serializer.py`, `layout_reading_order_resolver.py`, `layout_region_builder.py`
(the largest file in the package at 157 LOC), `page_orientation_resolver.py`, and the `models/`
dataclasses — have no direct unit test. `page_orientation_resolver.py`'s "square" branch is never
exercised anywhere. `docling_layout_metadata_builder.py`, the integration seam between Docling
raw items and the layout analyzer, has no test file at all. `docling_toc_table_row_reconstructor.py`
was heavily rewritten (+103 net lines) with no test file before or after this commit. The
existing `document_graph_reader.py` test was not updated to assert anything about
`parallel_stream_rows` or the layout fields.

## D. Enterprise-quality risks

1. **Duplicated, divergent lane-detection algorithms** (`LayoutLaneDetector` vs.
   `ParallelTableStreamClusterer`) solve the same geometric problem with unrelated algorithms,
   thresholds, and data granularity, and never share code or cross-check results — a real
   maintenance hazard, since a future fix to one will silently not apply to the other.
2. **~15 hardcoded, non-configurable magic-number thresholds** across six new files
   (`LayoutLaneDetector`'s boundary ratios, `ParallelTableStreamClusterer`'s gap/size
   constants, `ParallelTableQualityEvaluator`'s scoring weights, `DoclingParallelTableReconstructor`'s
   density thresholds, `DoclingTemplateDuplicateColumnCollapser`'s match ratios,
   `FrontMatterPageClassifier`'s body-text minimums) — none tunable without a code change, and
   several are exactly the kind of value that will need per-corpus tuning, the tuning risk the
   plan itself warned against, just expressed as numbers instead of phrase lists.
3. **English-only hardcoded literals inside structural logic** (see section A) — a real
   portability defect for non-English manuals.
4. **A six-stage row-repair pipeline with no documented interaction contract**: TOC
   reconstruction → single-column reconstruction → repeated-cell collapse → duplicate-column
   collapse → sparse continuation-row merge → interval repair, each independently mutating the
   row grid with its own heuristics (including another English-only lexical list of "open-ending"
   words in the continuation merger). Ordering matters, but no test exercises the full chain
   end-to-end with adversarial or conflicting inputs.
5. **Continued reliance on brittle substring matching against Docling's label vocabulary**
   (`"table" in label`, `"picture" in label or "image" in label`) rather than a typed label enum
   — inherited style, extended rather than fixed by the new layout package.
6. One coincidentally-safe edge case: `ParallelTableStreamClusterer` floors its gap threshold at
   `36.0` even for a zero-width table, so it does not crash today, but the safety is implicit
   rather than asserted — a future change to the upstream minimum-cluster-size constant could
   silently reintroduce a crash on an empty sequence downstream.

## E. Surprising findings

- Two unrelated "front matter" detectors now coexist with no shared concept between them (see
  section A, Phase 2).
- The plan document itself contains a self-graded "Implementation Progress Update" written in
  place — an accurate but optimistic self-assessment, per this audit, except for the
  "region-aware" framing addressed above.
- `TableCellSpan` gained its own optional bbox/page fields specifically for table-level
  reconstruction, entirely separate from the page-level bbox model — both ultimately derived from
  the same Docling provenance data, extracted twice via two different code paths.
- The commit bundles unrelated binary changes (the SQLite DB and local Qdrant storage) alongside
  code changes, meaning checking out this commit and re-ingesting will not reproduce a clean
  state independent of whatever was already ingested at commit time.
- The plan names `scripts/export_document_table_assets.py` and `scripts/debug_parse_document.py`
  as required Phase 6 verification surfaces, but the commit touches neither — the new
  layout/parallel-stream metadata currently has no way to be inspected via the project's existing
  debug tooling, the very tooling the plan's own evidence sections were built from.
