# Table Handling Enterprise-Standard Audit

## Status

Audit conducted 2026-07-14 across the full table parsing/structure-detection/hydration/chunking pipeline, following the work tracked in `table_structure_enterprise_upgrade_plan.md`. Method: four parallel code audits (docling parsing/extraction, shape-detection layer, QA/extraction hydration and typed projections, chunking/document-graph propagation), each instructed to verify claims with runnable reproductions rather than static reading alone. The two highest-severity findings were independently re-verified by direct reproduction before being written up here.

This document is the finding list plus the implementation plan. Implementation status is tracked inline per item as work lands.

**Implementation pass (2026-07-14): F1-F8 implemented and verified, each with a direct reproduction, a regression test, and a full green `tests/unit` run before moving to the next item. F9 investigated and confirmed real but deferred (see its section). F10/F11 deferred as originally scoped.**

---

## Executive Summary

The table pipeline is functionally solid for the shapes that were adversarially tested during the recent upgrade work (troubleshooting, performance-curve, specification-matrix false positives — all fixed with regression tests as of this audit). This scan found real, reproducible gaps in areas not yet stress-tested, plus one architecturally significant incomplete phase (chunking propagation of the newer structural fields), consistent with what `table_structure_enterprise_upgrade_plan.md` already lists as "not started."

Two findings are data-integrity issues with direct, demonstrated real-world impact:
- Unrelated tables can be silently merged into one logical family through a transitive bridging effect.
- The single most common real-world spare-parts table layout (cleanly split into separate columns) loses its Part Number field entirely.

Everything else is either a narrower correctness gap, a design inconsistency between sibling components, or a test-coverage hole. No crashes were found on any adversarial input tried (empty tables, ragged rows, huge row counts, all-empty cells) — the code is defensively written even where coverage is thin.

---

## Findings

### F1 — Logical table families can silently merge unrelated tables (CONFIRMED, HIGH SEVERITY)

`src/application/workflows/parsing/tables/logical_table_family_resolver.py`

`_continues_family` only ever compares the *immediately preceding* table in a candidate family to the current one — never back to the family's first (anchor) table. A "bridge" table with a generic, headerless shape (e.g. a bare `Parameter | Value` table with no distinguishing umbrella title) that is independently compatible with both of two otherwise-unrelated neighbors causes all three to be merged into a single logical family.

Reproduced directly:
```
Table A: "Bearing Specifications" / Parameter | Value / Bore=25mm
Table B: (no umbrella) Parameter | Value / Grease type=Lithium
Table C: "Motor Specifications" / Parameter | Value / Voltage=400V

-> A, B, and C all get logical_table_family_id="table_family_A", family_total=3
```

Downstream, `LogicalTableFamilyRowMerger`/hydration would combine bearing-spec rows and motor-spec rows into one presented "table" for QA and extraction — a real content-corruption risk for the common real-world pattern of several small spec tables placed close together in a manual.

No existing test constructs a 3+ table family or a bridging scenario; both `test_logical_table_family_resolver.py` and `test_table_header_compatibility_matcher.py` only cover 2-table chains.

**Fix direction**: require compatibility against the family anchor (first table), not just the previous table, before extending a family past 2 members — or require the whole chain to be pairwise-compatible in addition to head-compatible. Needs a design decision on which anchor rule to use; implement with tests covering the exact bridging scenario above (must NOT merge) alongside the existing legitimate multi-page continuation scenarios (must still merge).

**Status**: implemented.

### F2 — Spare-parts tables lose Part No./Service Package on the common columnar layout (CONFIRMED, HIGH SEVERITY)

`src/domain/assets/table_rows/spare_parts_table_normalizer.py`

`_parse_explicit_row`/`_seed_tokens` only recognize a position+quantity pair when both are whitespace-packed into a *single cell* (the merged-cell Docling artifact case, e.g. `"0010 1 Pce"`). When a table is already cleanly split into separate columns (`Pos | Qty | Unit | Description | Part No` — arguably the more common real-world shape when Docling's cell matching works correctly), no single cell has 2+ tokens, so the explicit-row path never fires. Parsing falls back to `_parse_free_form_row`, which has no part-code logic at all and dumps everything past the unit token into `description`.

Reproduced directly:
```
rows = [['Pos','Qty','Unit','Description','Part No'],
        ['10','2','Pce','Hex bolt M8x20','900.123.456']]

-> headers: ['Quantity','Unit','Description','Part No.','Position']
-> row: ['2','Pce','Hex bolt M8x20 900.123.456','','10']
```
`Part No.` is empty for every row; the real part number is silently absorbed into `Description`.

Only the merged-cell path has test coverage (`test_spare_parts_table_normalizer.py`); the plain columnar case is untested and broken.

**Fix direction**: add a genuinely columnar parse path — when the header row maps distinct columns to position/quantity/unit/description/part_no (via the same `_FIELD_MARKERS` header-mapping approach already used elsewhere in this codebase, e.g. `TroubleshootingTableNormalizer`), read each field directly from its own column instead of requiring the merged-cell token pattern. Keep the merged-cell path as a fallback for when no such column mapping exists.

**Status**: implemented.

### F3 — Shape-summarizer ordering can hide a more-correct classification (CONFIRMED — fixed as part of F5's underlying detector, not a routing change)

`src/application/workflows/parsing/tables/structure/table_structure_summary_builder.py`

Reproduced directly: a bolt-torque spec table keyed by diameter columns "6"/"8"/"10"/"12" (identical values on both header rows, since there's no unit to convert) was misclassified as `PERFORMANCE_CURVE_MATRIX` before `SpecificationMatrixStructureSummarizer` ever got a chance to run.

**Root cause turned out to be the curve detector's own precision, not the ordering** — a genuine curve axis point is the same physical value in two *different* units (e.g. "1"/"16.6"), so `PerformanceCurveMatrixDetector._has_curve_block` now requires at least one dual-numeric header column to actually differ between the two rows (rejecting the case where every column repeats the identical value on both rows, which is a discrete variant axis, not a curve). With that fix, the bolt-torque table now falls through to `RECORD_TABLE` (a safe, non-corrupting outcome — `SpecificationMatrixStructureSummarizer` still declines it too, via its own `numeric_header_count` guard, a separate, already-conservative check not touched here).

**Status**: implemented (fixing the curve detector's own precision closed this — no separate ordering/confidence-comparison change was needed). Regression test: `test_does_not_detect_a_discrete_numeric_variant_axis_repeated_on_both_header_rows` in `test_performance_curve_matrix_detector.py`.

### F4 — `SpecificationMatrixStructureSummarizer`'s interval exclusion is over-broad (CONFIRMED PLAUSIBLE)

`src/application/workflows/parsing/tables/structure/specification_matrix_structure_summarizer.py` (`_has_interval_header_signal`)

Reuses the maintenance-schedule single-letter header set (`d`, `w`, `m`, `q`, `s`, `a`) to decide "this looks like an interval column, decline specification_matrix." A genuine spec table with a bare dimension/variant column literally named `"A"` (common in engineering drawings comparing variants A/B/C) gets wrongly excluded.

**Fix direction**: require more than a single-letter match — e.g. only exclude on the *word* "interval" or a full schedule word ("daily", "weekly", ...), not the bare single-letter D/W/M/Q/S/A set, which is a much better fit checked elsewhere (`count_interval_columns` already gates on `>= 2` interval-like columns for the same table, which is a stronger, safer signal than a single-letter substring match here).

**Status**: implemented. `_has_interval_header_signal` no longer delegates to `looks_interval_header`'s single-letter membership check; it now matches only the literal word "interval", full schedule words, "every ", or hour/week/month/year substrings. Regression test: `test_detects_a_spec_matrix_with_a_bare_single_letter_variant_column`.

### F5 — Curve detection depends entirely on one row (CONFIRMED PLAUSIBLE)

`src/domain/assets/table_rows/performance_curve_matrix_detector.py`

`detect()` uses only `rows[2]` as the canonical sample row for the whole curve-block scan; a single blank cell in that one row (e.g. a sensor reading not taken at the highest flow point) breaks the scan for the entire table, even if later rows are fully populated.

**Fix direction**: try more than one candidate sample row (e.g. the first N data rows) before giving up on a given `start_index`, since Docling-parsed data legitimately has occasional blank cells.

**Status**: implemented. `detect()` now tries up to 5 candidate data rows per `start_index` before giving up. Regression test: `test_detects_curve_even_when_the_first_data_row_has_a_sparse_column`.

### F6 — QA vs. extraction representation drift via `chunk_type` handling (CONFIRMED PLAUSIBLE)

`src/application/workflows/extraction/batching/table_payload/spare_parts_table_payload_builder.py`, `troubleshooting_table_payload_builder.py` vs. their QA-side `projections/` counterparts.

Extraction payload builders call `normalize(..., chunk_type=None)` unconditionally; QA projection builders pass the real `source.chunk_type`. A table classified only via `chunk_type` (no `table_category` metadata yet) gets a proper typed projection in QA but falls through to the generic dump at extraction time for the identical table.

**Fix direction**: thread `chunk_type` through the extraction-side payload builders the same way the QA-side ones already do — this is a small, mechanical parity fix once the call sites are identified.

**Status**: implemented. `extraction_table_chunk_hydrator.py` now passes `chunk.chunk_type` through `ExtractionTablePayloadRenderer.render()` into every payload builder's `build(table, chunk_type=...)`. Confirmed via before/after reproduction: a table classified only by `chunk_type=TROUBLESHOOTING` (no `table_category`) previously fell to the generic "Structured table records:" payload; now correctly produces "Structured troubleshooting records:". Regression test: `test_hydrate_table_chunks_uses_chunk_type_to_render_typed_payload_without_table_category`.

### F7 — `docling_table_extractor.py`: `0` end-offset treated as falsy (CONFIRMED PLAUSIBLE)

`extract_dimensions` uses `coerced_end or (start + 1)`. Since `0` is falsy in Python, a legitimate `end_row_offset_idx == 0`/`end_col_offset_idx == 0` is silently discarded in favor of the fallback, producing a wrong `row_count`/`column_count`.

**Fix direction**: `coerced_end if coerced_end is not None else (start + 1)`.

**Status**: implemented via a new `_resolve_offset_end` helper with an explicit `is not None` check. Note: the true end-to-end scenario (a real `end_row_offset_idx == 0`) does not appear to be reachable through Docling's actual offset convention (exclusive end, so a real single-row-0 cell would report `end == 1`, never `0`) — this is a genuine code-smell fix (removes a latent falsy-vs-None trap for the full theoretical input domain) rather than a demonstrated live production bug. New test file `test_docling_table_extractor.py` (none existed before) covers the happy path plus this edge case directly.

### F8 — Unbounded grid allocation in `docling_table_row_grid_builder.py` (CONFIRMED PLAUSIBLE, potential hang/DoS)

No upper bound on `max_row`/`max_col` before allocating the row grid. A single malformed cell span with a very large offset causes a large, slow allocation with no config guard, no timeout.

**Fix direction**: add a sane upper bound (config-exposed, matching the project's existing settings pattern) and fail loudly (raise a parsing error) rather than attempt the allocation, consistent with `docling_document_normalizer.py`'s existing "fail loud" top-level policy.

**Status**: implemented. New setting `DOCLING_MAX_TABLE_GRID_CELLS` (default 200,000 — generous for any real table) in `docling_settings.py`; `DoclingTableRowGridBuilder._guard_grid_size` raises `DocumentNormalizationError` before allocating if the implied grid exceeds it. Verified directly: a single cell with `end_row_offset_idx=2_000_000` now raises immediately instead of allocating. Regression test: `test_build_rows_fails_loudly_on_an_implausibly_large_malformed_span`.

### F9 — `parsed_asset_factory.py`: column-dropping geometry mismatch (CONFIRMED PLAUSIBLE)

`drop_globally_empty_columns` is applied to `rows` but not reflected in `cell_spans`/`column_count`, which retain original (pre-drop) column indices. Any consumer assuming `column_count == len(rows[i])` for a table with an empty column would be wrong.

**Fix direction**: verify actual consumer impact first (does anything currently index `cell_spans` by column position against the post-drop `rows`?) before deciding whether this needs a fix or just a clarifying comment.

**Investigation outcome**: confirmed real. `TableHeaderPathBuilder._span_text_for_cell` (used by family header-signature matching, see F1's area) looks up header text by `(row_index, column_index)` against `table.cell_spans`, cross-referenced against `column_count = max(table.column_count, max(len(row) for row in table.rows))` — both of which retain pre-drop indices/counts while `rows` is post-drop. Confirmed `drop_globally_empty_columns` does shift column positions (`[['A','','B']] → [['A','B']]`, dropping index 1). The likely blast radius is narrower than F1/F2 though: `_path_for_column`'s span lookup has a same-cell fallback to reading `table.rows[row_index][column_index]` directly when no span matches, so a geometry mismatch mostly just loses the span-based enrichment for the shifted column(s) rather than reliably producing wrong data — it would only produce actively wrong output if a stale span's shifted index happens to coincidentally land on a different real column after the drop.

**Status**: not fixed in this pass. A correct fix requires re-indexing `cell_spans`' column positions (and adjusting `column_count`) whenever `drop_globally_empty_columns` removes a column — a small column-index-remapping utility, not a one-line change, and a different risk/effort profile than F1-F8's targeted fixes. Deferred as a follow-on item; flagged here with enough detail (exact mismatch mechanism, confirmed repro of the shift, and the fallback that bounds its real-world impact) to pick up directly.

### F10 — Phase 4 chunking propagation is genuinely incomplete (CONFIRMED, matches the upgrade plan's own "not started")

`src/application/workflows/parsing/builders/chunking/builders/fragment/table_fragment_builder.py` (`table_metadata()`)

`table_shape`, `table_structure_quality`, `header_paths`, `axis_summary` are correctly computed and persisted on `TableAsset`/`parser_metadata.extra`, but `table_metadata()` — the sole bridge into chunk construction — only forwards the older `table_category`/`table_category_confidence`/family fields. Verified directly: constructing a fake element with all four new fields populated in `parser_metadata.extra` and calling `table_metadata()` returns none of them. `ChunkFragment`, `ChunkPayload`, and `DocumentChunk` have no fields for them at all; the DB chunk mapper has no analog either. Ordering itself is safe — structure resolution runs strictly before chunk building, so this isn't a race, purely a propagation gap.

**Fix direction**: this is the plan's own Phase 4 — thread the four fields through `TableFragmentBuilder` → `ChunkFragment`/`ChunkPayload` → `DocumentChunk` → DB mapper, plus reconciliation logic in `logical_table_family_fragment_builder.py` for merging across family members (currently only copies from the lead element, with no merge for any field).

**Status**: not started (tracked as its own multi-file phase, not attempted in this pass — significant scope, see Implementation Plan below).

### F11 — Test coverage gaps (no crashes found, but coverage is thin)

Zero test files exist for: `docling_table_extractor.py`, `parsed_asset_factory.py`, `asset_metadata_synchronizer.py`, `table_cell_span.py`, `GenericRecordStructureSummarizer` (isolated), `MaintenanceScheduleStructureSummarizer` (isolated), `maintenance_schedule_table_projection_builder.py`, `specification_matrix_table_projection_builder.py`, `logical_table_family_fragment_builder.py`, `graph_chunk_builder.py`.

**Status**: addressed opportunistically alongside each fix above; a dedicated sweep for the remaining untouched files is out of scope for this pass.

### F12 — Minor / style (not blocking)

- `_INTERVAL_HEADER_PATTERN` in `docling_table_row_grid_builder.py` hardcodes D/W/M/Q/S/A schedule vocabulary directly in the generic row-grid builder — the project's own "no document-specific value rules" principle would put this in an isolated, swappable shape-detection module instead. Not fixed in this pass (working, just architecturally misplaced).
- No feature flag gates the new structure-detection layer (`TableSemanticResolver`'s shape/quality/header-path computation), unlike every other major feature shipped in this codebase's history (which defaulted off). Not fixed in this pass — would need a design decision on default behavior.
- `table_semantic_rule_evaluator.py` (354 lines, pre-existing, untouched by the recent table-structure work) already exceeds the repo's ~300-LOC split convention. Flagged for awareness, not in scope here.

---

## Implementation Plan

Ordering rationale: fix confirmed data-integrity bugs with demonstrated real-world impact first (F1, F2), then the smaller confirmed-plausible correctness gaps (F3-F9) in roughly ascending effort, leaving the larger structural phase (F10, chunking propagation) and the broad test-coverage sweep (F11) as explicitly separate, larger follow-on work given their scope.

1. **F1** — logical table family anchor-validation fix + tests (bridging scenario + existing continuation scenarios must both pass). **Done.**
2. **F2** — spare-parts columnar parsing path + tests (columnar case + existing merged-cell case must both pass). **Done.**
3. **F3** — verify the curve/spec ordering-suppression scenario with a constructed reproduction; fix via tightened curve detection or confidence-based selection, whichever is more surgical once confirmed. **Done** — root cause was curve-detector precision, not ordering; closed by the same fix as F5's neighbor.
4. **F4** — narrow the interval-exclusion check in the specification-matrix summarizer. **Done.**
5. **F5** — make curve detection tolerant of one sparse sample row. **Done.**
6. **F6** — thread `chunk_type` through extraction-side payload builders to match QA-side behavior. **Done.**
7. **F7** — fix the falsy-zero bug in `docling_table_extractor.py`. **Done** (new test file added — none existed before).
8. **F8** — add a config-exposed upper bound + loud failure for row-grid allocation. **Done.**
9. **F9** — investigate real consumer impact; fix or document as appropriate. **Investigated, confirmed real, deferred** — needs a column-index remapping utility, a different scope than F1-F8's targeted fixes.
10. **F10** — separate, larger phase: thread the four newer structural fields through chunking into `DocumentChunk`/DB mapper. **Deferred**, as originally scoped — revisit as its own dedicated effort given the number of files and the need for family-level reconciliation logic.
11. **F11** — broad test-coverage sweep for the remaining untouched files. **Deferred** as a dedicated pass; coverage was added opportunistically alongside F1-F8 (new test files for `logical_table_family_resolver`, `spare_parts_table_normalizer`, `performance_curve_matrix_detector`, `specification_matrix_structure_summarizer`, `extraction_table_chunk_hydrator`/extraction workflow, `docling_table_extractor` (new), `docling_table_row_grid_builder`).

Every fix shipped with a regression test reproducing the exact failure mode found, verified against a full green `tests/unit` run before moving to the next item. Final state: 8 of 9 targeted findings (F1-F8) fixed and verified; F9 investigated and documented for a follow-on pass; F10/F11 remain explicitly out of scope for this pass as originally planned.
