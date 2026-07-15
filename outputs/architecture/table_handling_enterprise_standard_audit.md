# Table Handling Enterprise-Standard Audit

## Status

Audit conducted 2026-07-14 across the full table parsing/structure-detection/hydration/chunking pipeline, following the work tracked in `table_structure_enterprise_upgrade_plan.md`. Method: four parallel code audits (docling parsing/extraction, shape-detection layer, QA/extraction hydration and typed projections, chunking/document-graph propagation), each instructed to verify claims with runnable reproductions rather than static reading alone. The two highest-severity findings were independently re-verified by direct reproduction before being written up here.

This document is the finding list plus the implementation plan. Implementation status is tracked inline per item as work lands.

**Implementation pass (2026-07-14): F1-F8 implemented and verified, each with a direct reproduction, a regression test, and a full green `tests/unit` run before moving to the next item. F9 investigated and confirmed real but deferred (see its section). F10/F11 deferred as originally scoped.**

**Implementation pass (2026-07-15): F13 (interval-header false-positive misread from a real corpus sweep) implemented and verified. F9 implemented and verified against the real 23-document corpus in the DB (direct DB retrieval, not LLM-based) — confirmed at scale (37/592 real stored tables affected) and fixed with a column-index remap plus regression tests. A second, unrelated geometry anomaly (F9b) was discovered during F9's corpus verification, investigated to root cause, and fixed. F10 (chunking propagation) implemented — all four structural fields now flow through every layer down to the DB, including family-level reconciliation. F11 (test-coverage sweep) completed as its own dedicated pass — every remaining zero-coverage file from the original list now has a test file. F9b's root cause: `docling_document_normalizer.py` measured `row_count`/`column_count` from the pre-repair Docling cell grid while `table_rows` reflected the post-repair (TOC/single-column reconstructed) grid — now both are derived from the same final `rows`. Full `tests/unit` suite: 2733 passed, 0 failed.**

---

## Executive Summary

The table pipeline is functionally solid for the shapes that were adversarially tested during the recent upgrade work (troubleshooting, performance-curve, specification-matrix false positives — all fixed with regression tests as of this audit). This scan found real, reproducible gaps in areas not yet stress-tested, plus one architecturally significant incomplete phase — chunking propagation of the newer structural fields (F10), consistent with what `table_structure_enterprise_upgrade_plan.md` listed as "not started" — which has since been implemented in this pass.

Four findings are data-integrity issues with direct, demonstrated real-world impact:
- Unrelated tables can be silently merged into one logical family through a transitive bridging effect.
- The single most common real-world spare-parts table layout (cleanly split into separate columns) loses its Part Number field entirely.
- A column-dropping geometry mismatch left header-span coordinates stale relative to the actual stored row width — confirmed at scale against the real 23-document DB corpus (37/592 stored tables affected).
- A separate, opposite-direction dimension mismatch (F9b): `row_count`/`column_count` measured from the pre-repair Docling cell grid while `table_rows` reflects Docling's own post-repair (TOC/single-column-reconstructed) grid — confirmed on 9 tables via `column_count` and 13 more via `row_count` across the same real corpus.

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

### F9 — `parsed_asset_factory.py`: column-dropping geometry mismatch (CONFIRMED, HIGH SEVERITY — real-corpus verified) — Status: implemented

`drop_globally_empty_columns` is applied to `rows` but not reflected in `cell_spans`/`column_count`, which retain original (pre-drop) column indices. Any consumer assuming `column_count == len(rows[i])` for a table with an empty column would be wrong.

**Investigation outcome**: confirmed real, then confirmed at scale against the live corpus. `TableHeaderPathBuilder._span_text_for_cell` (used by family header-signature matching, see F1's area) looks up header text by `(row_index, column_index)` against `table.cell_spans`, cross-referenced against `column_count = max(table.column_count, max(len(row) for row in table.rows))` — both of which retain pre-drop indices/counts while `rows` is post-drop.

**Corpus verification (real data, not synthetic — direct DB retrieval, no LLM involved)**: wrote a one-off scan (`DocumentCatalogService.list_documents()` → `DocumentLookupService.get_document_graph(document_id)` → iterate `graph.tables.values()`) over all 23 documents currently persisted in the database. Scanned 592 real stored table assets; found 37 with `declared column_count != actual row width`. Of those, ~28 matched this finding's exact mechanism precisely (`declared_column_count > actual_row_width`, with the largest `cell_spans` column index landing exactly at `declared_column_count - 1` — the fingerprint of stale pre-drop span coordinates persisted permanently in the DB). Real example: `2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate`, table `table_26805c44c62f4a8d88cc901f1930a69d` — `declared_column_count=22`, actual stored row width=14, max stored span `col_end=21`. This confirms the bug is not a theoretical edge case: roughly 4.7% of real persisted tables in this corpus carry the geometry mismatch.

The remaining ~9 of the 37 hits are a *different* anomaly (`declared_column_count < actual_row_width`, e.g. `declared=1, actual_row_width=3` on TOC-style "Number | Title | Page" tables) — this cannot come from column-dropping (which only ever shrinks row width, never grows it past the original), so it has a different root cause upstream of this fix and is **not** addressed here. Logged as a new open item, not fixed or further investigated in this pass — see F9b below.

**Fix implemented**: `drop_globally_empty_columns` (`src/domain/assets/table_rows/table_row_patterns.py`) now exposes the kept-column-index computation as `compute_kept_column_indexes`, shared with the drop function so both operate on identical indices. `ParsedAssetFactory.build_table_asset` (`src/application/workflows/parsing/builders/document_graph/parsed_asset_factory.py`) now computes `kept_column_indexes` once alongside the cleaned rows, and whenever a column was actually dropped: (1) decrements `column_count` by the number of dropped columns, and (2) remaps every `TableCellSpan`'s `col_start`/`col_end` via a bisect-based index remap (`_remap_cell_spans`) — a span whose endpoints fall on a kept column shifts to that column's new position; a span that lived entirely inside a dropped (globally-empty) column is removed outright rather than left dangling. Tables with no dropped columns are returned byte-identical to before (verified by a dedicated regression test), so this only changes behavior for the previously-broken case.

Verified directly: reproduced the F1-style bridging-adjacent case (`[["Parameter", "", "Value"], ["Bore", "", "25mm"]]` with spans on the dropped middle column) — before the fix, `TableHeaderPathBuilder.build_paths` would query the wrong post-drop column index against pre-drop span coordinates; after the fix it correctly resolves `(("parameter",), ("value",))`. New test file `tests/unit/application/workflows/parsing/builders/document_graph/test_parsed_asset_factory.py` (none existed before, closing part of F11's coverage gap for this file) covers: drop-and-remap, span-fully-inside-a-dropped-column removal, no-op when nothing is dropped, and the end-to-end `TableHeaderPathBuilder` resolution. Full `tests/unit` suite: 2682 passed, 0 failed.

**Caveat**: this is a code-level fix; tables already persisted in the DB before this fix keep their stale pre-drop `cell_spans`/`column_count` until the source document is re-ingested. No backfill/migration was run as part of this pass — flag if a corpus-wide re-ingestion or a targeted backfill script is wanted.

### F9b — Docling-derived `column_count`/`row_count` metadata can itself be stale relative to the real (post-repair) row shape (CONFIRMED, HIGH SEVERITY) — Status: implemented

Found while verifying F9 against the real corpus: 9 of the 592 scanned tables have `declared_column_count < actual_row_width` (e.g. `declared_column_count=1` while `table.rows` entries have 2-3 cells), all on simple list/TOC-style tables (`Number | Title | Page`, `P&ID Pos Nr. | Service Function Type | Part No.`). This is the opposite direction from F9 and cannot be produced by `drop_globally_empty_columns` (which only ever removes columns, never adds row width beyond the original).

**Root cause, confirmed by direct reproduction**: `docling_document_normalizer.py::_build_metadata` computes `table_rows` and `row_count`/`column_count` from the *same* Docling item but at two different processing stages. `rows = self.table_extractor.extract_rows(item)` returns the **post-repair** grid — `DoclingTableRowGridBuilder.build_rows()`'s final step calls `DoclingTableRowRepairer.repair_rows()`, which chains `DoclingTocTableRowReconstructor` and `DoclingSingleColumnStructuredTableReconstructor` on top of `DoclingRepeatedCellRowCollapser`/`DoclingIntervalTableRowRepairer`. The first two reconstructors take a genuinely single-column Docling table (Docling failed to detect real column boundaries — common for TOC pages and merged-cell spare-parts lists) and **split each row's merged text into multiple new cells**, sometimes inserting a synthetic header row. Separately, `row_count, column_count = self.table_extractor.extract_dimensions(item)` measures the **pre-repair** raw Docling cell grid — captured before any of that reconstruction happens. Reproduced directly: a synthetic single-column TOC table (`["1 Introduction 1"]`, `["2 Installation 5"]`, `["3 Maintenance 12"]`, one merged cell per row) produces `column_count=1, row_count=3` from `extract_dimensions`, while the repaired `table_rows` is `[["Number","Title","Page"], ["1","Introduction","1"], ...]` — width 3, count 4 — exactly matching the real corpus signature (`declared=1` vs `actual_row_width=3`).

Also checked the equivalent `row_count` mismatch (the original corpus scan only checked `column_count`) — a follow-up corpus scan found **13 more real tables** with `declared_row_count != len(table.rows)`, for the identical reason: the TOC reconstructor's synthetic header row changes row count too, not just column count.

**Fix implemented**: `docling_document_normalizer.py::_build_metadata` now derives `row_count`/`column_count` from the actual, final `rows` (`row_count = len(rows)`, `column_count = max(len(row) for row in rows)`) whenever `rows` is non-empty, overriding the pre-repair `extract_dimensions()` values — the same "trust the final persisted structure" principle F9's fix already established for `cell_spans`. When `rows` is empty, the pre-repair `extract_dimensions()` values are kept as a fallback (unchanged behavior for tables with no row-grid signal).

Verified directly: the synthetic single-column TOC repro above now correctly reports `column_count=3, row_count=4` via `DoclingDocumentNormalizer._build_metadata`. New regression test `test_table_dimensions_reflect_post_repair_rows_not_the_raw_single_column_grid` (`_test_docling_document_normalizer_part1.py`) added — none of the existing `docling_document_normalizer`/`docling_table_extractor`/`docling_table_row_repairer` tests needed changes (all still green), confirming the fix only changes behavior for the previously-broken mismatch case. Full `tests/unit` suite: 2733 passed, 0 failed.

**Caveat**: this is a code-level fix at parse time; tables already persisted in the DB before this fix keep their stale `row_count`/`column_count` until the source document is re-ingested. No backfill/migration was run as part of this pass.

### F10 — Phase 4 chunking propagation is genuinely incomplete (CONFIRMED, matches the upgrade plan's own "not started") — Status: implemented

`src/application/workflows/parsing/builders/chunking/builders/fragment/table_fragment_builder.py` (`table_metadata()`)

`table_shape`, `table_structure_quality`, `header_paths`, `axis_summary` are correctly computed and persisted on `TableAsset`/`parser_metadata.extra`, but `table_metadata()` — the sole bridge into chunk construction — only forwards the older `table_category`/`table_category_confidence`/family fields. Verified directly: constructing a fake element with all four new fields populated in `parser_metadata.extra` and calling `table_metadata()` returns none of them. `ChunkFragment`, `ChunkPayload`, and `DocumentChunk` have no fields for them at all; the DB chunk mapper has no analog either. Ordering itself is safe — structure resolution runs strictly before chunk building, so this isn't a race, purely a propagation gap.

**Fix implemented (2026-07-15)**: threaded all four fields end-to-end through every layer named in the original fix direction, plus one call site the original write-up didn't name:

- `TableFragmentBuilder.table_metadata()` now reads `table_shape`/`table_structure_quality` (via the existing `coerce_float`) and reads/cleans `table_header_paths_json` → `header_paths` and `table_axis_summary` → `axis_summary` from `parser_extra` (mapping the `_json`-suffixed `parser_extra` key names onto the `TableAsset`-matching attribute names, since those differ — noted as a trap in the original investigation).
- A new `TableFragmentBuilder.merge_family_table_metadata()` reconciles the four fields across every member of a logical table family, reusing the exact merge rules already established on the QA side (`table_evidence_hydrator.py`'s `_resolve_table_shape`/`_resolve_table_structure_quality`/`_merge_header_paths`/`_merge_axis_summary`) for consistency with a sibling component rather than inventing a new policy: first non-null wins for `table_shape`/`table_structure_quality`, header paths are deduped-unioned in encounter order, axis summary keys are first-wins-per-key unioned.
- `LogicalTableFamilyFragmentBuilder._build_family_fragment` — previously copied `table_category`/`table_category_confidence` from `family_elements[0]` only (the exact "lead-only, no merge" gap called out in the original fix direction) — now calls `merge_family_table_metadata(family_elements)` and sets all four fields from the merged result.
- `ChunkFragmentBuilder._enrich_structured_table_fragments` had the identical lead-element-only pattern for the "structured section" table path (not named in the original write-up, found while implementing) — fixed the same way.
- `ChunkFragmentBuilder._build_fragment_from_element` (the single-element, non-family table path) now forwards the four fields from `table_metadata()`.
- `ChunkFragment`, `ChunkPayload`, `DocumentChunk` dataclasses each gained the four fields (`table_shape: str | None`, `table_structure_quality: float | None`, `header_paths: list[list[str]]`, `axis_summary: dict[str, str]`), and `ChunkPayloadFactory.build_payload`/`GraphChunkBuilder.build_chunks` thread them through from fragment → payload → domain chunk, mirroring the exact `table_category` plumbing pattern already in place at each site.
- `ChunkORM` gained `table_shape` (String), `table_structure_quality` (float), `header_paths_json`/`axis_summary_json` (Text, JSON-encoded — `header_paths` and `axis_summary` are structured, not flat string lists, so they get dedicated `_dump_header_paths`/`_load_header_paths`/`_dump_axis_summary`/`_load_axis_summary` helpers on `ChunkMapper` rather than reusing the flat-list helpers). `schema_management.py`'s `_ensure_sqlite_column` calls were extended for all four new `chunks` columns, matching the exact backward-compatible-column-addition pattern already used for `table_category` etc. (this codebase does not use Alembic migrations for these columns in practice — confirmed no existing migration touches any of the `chunks` table's `table_category`-family columns either, so the hand-rolled SQLite patching is the established, consistent mechanism here, not a shortcut).

**Verified**: full `tests/unit` suite green (2692 passed, 0 failed, up from 2682 before this fix — 10 new tests added). New/extended tests: `test_table_fragment_builder.py` (metadata forwarding + defaults + family-merge helper, both first-non-null and union behavior), `test_chunk_fragment_builder.py` (end-to-end family-merge assertion through `build_section_fragments`), `test_chunk_payload_factory.py` (forwarding + no-table-fragment defaults), `test_chunk_mapper.py` (DB round-trip + absent-field defaults), and a new `test_graph_chunk_builder.py` (previously zero coverage per F11 — payload→domain-chunk wiring, with and without the four fields set).

### F11 — Test coverage gaps (no crashes found, but coverage is thin) — Status: implemented

Zero test files existed for: `docling_table_extractor.py`, `parsed_asset_factory.py`, `asset_metadata_synchronizer.py`, `table_cell_span.py`, `GenericRecordStructureSummarizer` (isolated), `MaintenanceScheduleStructureSummarizer` (isolated), `maintenance_schedule_table_projection_builder.py`, `specification_matrix_table_projection_builder.py`, `logical_table_family_fragment_builder.py`, `graph_chunk_builder.py`.

**Status (2026-07-15)**: `docling_table_extractor.py`, `parsed_asset_factory.py`, and `graph_chunk_builder.py` were closed opportunistically as part of F7/F9/F10. The remaining seven files from the original list were addressed in a dedicated sweep:

- `test_table_cell_span.py` (new) — row/col span derivation (including the `max(1, ...)` floor for inverted start/end), `to_dict`/`from_dict` round-trip, `list_from_data`'s non-list/non-dict filtering.
- `test_asset_metadata_synchronizer.py` (new) — verifies every field `AssetMetadataSynchronizer.sync` writes onto `parser_metadata.extra` for both table and picture elements, that the four F10 structural fields are correctly omitted (not written as `None`/empty) when unset on the `TableAsset`, and that elements with no `parser_metadata` or a dangling `table_id` are safely skipped.
- `test_generic_record_structure_summarizer.py` (new) — the `None`-returning guards (too few rows, no data rows left after the header, single-column table, headers without alpha signal) plus two exact, hand-computed `quality_score` regression values (`0.80` and `0.70`) tied to specific combinations of the score's four additive components, so any future change to the scoring formula gets caught precisely rather than approximately.
- `test_maintenance_schedule_structure_summarizer.py` (new) — real schedule-code headers (`D`/`W`/`M`) run through the actual `TableMatrixDetector`/`TableRowCanonicalizer` dependencies (not mocked) to get a genuine `maintenance_schedule_matrix` classification, verifying the compact-code-to-full-word header expansion (`D`→`Daily` etc.), the `Notes`/`descriptor_axis` detection, and the non-matrix rejection path.
- `test_maintenance_schedule_table_projection_builder.py` (new) — `.project()` called directly (bypassing the `AnswerTableProjector` router) covering: too-few-rows and non-maintenance-table rejections, task/interval/notes column resolution with blank-row filtering, and component-column resolution.
- `test_specification_matrix_table_projection_builder.py` (new) — the `table_shape != "specification_matrix"` and too-few-rows guards, plus label/value row building, unit-column combination, notes-in-parentheses, and multi-value-column label qualification (`"Voltage (Min)"` / `"Voltage (Max)"`).
- `test_logical_table_family_fragment_builder.py` (new) — direct, isolated tests (distinct from F10's end-to-end assertion via `ChunkFragmentBuilder`) covering: no-family/empty-result, `excluded_element_ids` filtering, a full two-member family merge (rows, page min/max, table/element ids, and the F10 structural-field reconciliation), and two independent families coexisting in one section.

Verified: full `tests/unit` suite green (2728 passed, 0 failed, up from 2692 before this sweep — 36 new tests added, zero changes to production code in this pass).

### F13 — `count_interval_header_tokens` misreads stray words in garbled headers as schedule codes (CONFIRMED, HIGH SEVERITY) — Status: implemented

Found via corpus sweep of the real `maintenance_interval_table` category across all 23 ingested documents. `TableTextSignalMatcher.count_interval_header_tokens` (table_text_signal_matcher.py) tokenized each header cell on whitespace and counted a match if **any single token** equalled a bare D/W/M/Q/S/A schedule-code letter — including the English article "a" or a stray OCR letter "s" occurring anywhere inside a long, unrelated free-text sentence header. On a real, severely OCR-garbled troubleshooting cross-reference matrix (a rotated-header table in the FWC12 pump manual, symptom-vs-cause "x" marker grid), this produced `interval_header_count >= 2` purely from incidental words, causing `TableSemanticClassifier` (which checks `MAINTENANCE_INTERVAL_TABLE` before `TROUBLESHOOTING_TABLE`) to confidently (0.89) mislabel the table. Reproduced against 3 real corpus tables (2 in PURO 30, 1 in FWC12), all previously mislabeled `maintenance_interval_table` at 0.87-0.92 confidence.

**Fix**: `count_interval_header_tokens` now only credits the per-token fallback when **every** token in a header cell is itself a schedule-code token (mirrors `IntervalExpressionParser._looks_like_schedule_code_expression`'s intent) — this still matches genuine compact multi-code cells like `"M S A"` or `"Q Q"` (all tokens qualify) but no longer fires on long sentences that merely contain an incidental one-letter word. Verified against the 3 real repro tables (all now fall to honest `general_table`/0.4 instead of a wrong confident label) and against the existing compact-schedule-cell test case. Added `test_classify_does_not_treat_stray_letters_in_garbled_free_text_headers_as_schedule_codes` (test_table_semantic_classifier.py) as a permanent regression test. Full suite: 2678 passed, 0 failed.

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
9. **F9** — investigate real consumer impact; fix or document as appropriate. **Done** — verified at scale against the real 23-document DB corpus (37/592 tables affected, ~28 matching this exact mechanism), then fixed via a column-index remapping utility (`compute_kept_column_indexes` + `ParsedAssetFactory._remap_cell_spans`) with regression tests.
10. **F13** — fix the interval-header stray-token false-positive found via the corpus sweep. **Done.**
11. **F9b** — newly discovered during F9's corpus verification: `column_count`/`row_count` metadata itself stale relative to the actual row shape, unrelated to column-dropping. **Done** — root cause traced to `docling_document_normalizer.py::_build_metadata` measuring dimensions from the pre-repair Docling cell grid while `table_rows` reflects the post-repair (TOC/single-column-reconstructed) grid; fixed by deriving `row_count`/`column_count` from the final `rows` directly, with a direct reproduction and regression test.
12. **F10** — thread the four newer structural fields through chunking into `DocumentChunk`/DB mapper, plus family-level reconciliation. **Done** — `TableFragmentBuilder.table_metadata()` + new `merge_family_table_metadata()` → `LogicalTableFamilyFragmentBuilder`/`ChunkFragmentBuilder`'s two lead-only call sites → `ChunkFragment`/`ChunkPayload`/`DocumentChunk` → `ChunkORM`/`ChunkMapper` (JSON-encoded columns + `schema_management.py` patching), all verified with new/extended tests at every layer.
13. **F11** — broad test-coverage sweep for the remaining untouched files. **Done** — `docling_table_extractor`/`parsed_asset_factory`/`graph_chunk_builder` were closed opportunistically alongside F7/F9/F10; the remaining seven files (`asset_metadata_synchronizer`, `table_cell_span`, `GenericRecordStructureSummarizer`, `MaintenanceScheduleStructureSummarizer`, `maintenance_schedule_table_projection_builder`, `specification_matrix_table_projection_builder`, `logical_table_family_fragment_builder`) got new dedicated test files in this pass — 36 new tests, zero production-code changes.

Every fix shipped with a regression test reproducing the exact failure mode found (or, for F10, exercising the exact propagation path; for F11, exercising the previously-untested real behavior directly), verified against a full green `tests/unit` run before moving to the next item. Final state: F1-F11, F9b, and F13 all fixed/implemented and verified (F9 additionally verified at scale against the real DB corpus). Only F12 (minor/style items, one of which needs a product decision on default behavior) remains open, as originally scoped. Full `tests/unit` suite: 2733 passed, 0 failed.
