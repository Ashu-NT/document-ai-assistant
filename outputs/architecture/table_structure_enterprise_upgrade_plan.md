# Enterprise Table Structure Upgrade Plan

## Executive Summary

The current table pipeline is good at:

- detecting many tables
- preserving useful Markdown
- grouping continued tables into logical families
- hydrating full table families for extraction and QA

The current table pipeline is weak at:

- reconstructing multi-row and multi-column headers
- preserving merged-cell semantics
- distinguishing table **category** from table **shape**
- projecting matrix/curve tables into strongly typed structured evidence
- feeding the LLM a structure-aware representation instead of flattened pseudo key-value text

This is the main reason the PURO pump-curve example looks acceptable in Markdown but degrades into weak `header=value` lines in structured output.

The goal of this upgrade is to make table understanding first-class across parsing, chunking, extraction, retrieval, and answer generation without introducing dump files or document-specific rules.

## Current Implementation Status

### Completed

- Phase 1 settings exposure is implemented.
  - `src/config/settings/docling_settings.py`
  - `src/infrastructure/parsing/docling/docling_converter_factory.py`
  - `DOCLING_TABLE_STRUCTURE_MODE`
  - `DOCLING_TABLE_CELL_MATCHING`
- The first end-to-end typed shape is implemented for `performance_curve_matrix`.
  - `src/domain/assets/table_rows/performance_curve_matrix_detector.py`
  - `src/domain/assets/table_rows/performance_curve_matrix_normalizer.py`
  - `src/domain/assets/table_rows/structured_row_renderer.py`
  - `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
- Persisted table assets now carry an explicit `table_shape` when available.
  - `src/domain/assets/table_asset.py`
  - `src/application/workflows/parsing/builders/document_graph/parsed_asset_factory.py`
  - `src/application/workflows/parsing/builders/document_graph/asset_metadata_synchronizer.py`
  - `src/infrastructure/db/repositories/document/document_graph_reader.py`
- Debug table export now shows `table_shape`.
  - `scripts/export_document_table_assets.py`

### Partially implemented

- Phase 2 / Phase 3 foundation has started via a reusable structure-summary layer for the shapes we already detect safely.
  - `src/application/workflows/parsing/tables/structure/`
  - current summaries:
    - `maintenance_schedule_matrix`
    - `performance_curve_matrix`
- Persisted table assets now also begin carrying:
  - `table_structure_quality`
  - `table_header_paths_json`
  - `table_axis_summary`
- Document-level metadata now exposes `table_shape_counts` and a bumped `table_structure_schema`.

### Still remaining

- generic span-aware normalized table model for arbitrary merged headers
- continued-table header hierarchy reconstruction across pages
- typed QA projection package split by projector class
- extraction-side normalized table evidence payloads
- optional selective fallback table-structure provider

---

## Current Diagnosis

### What is already strong

- `src/infrastructure/parsing/docling/docling_converter_factory.py`
  - already enables Docling table structure extraction
  - already uses Docling table structure defaults, which in the installed runtime are `TableFormerMode.ACCURATE` and `do_cell_matching=True`
- `src/application/workflows/parsing/normalizers/docling_table_extractor.py`
  - extracts Markdown, row grid, dimensions, and raw cell spans
- `src/domain/assets/table_asset.py`
  - persists raw table content, `rows`, `cell_spans`, family ids, and table category
- `src/application/workflows/parsing/tables/logical_table_family_resolver.py`
  - already merges cross-page continued tables into logical families
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
  - already hydrates full logical table families for QA
- `src/application/workflows/extraction/batching/extraction_table_chunk_hydrator.py`
  - already hydrates full logical table families for extraction

### Where meaning is currently lost

- `src/application/workflows/parsing/normalizers/docling_table_row_grid_builder.py`
  - builds a flat row grid from spans
  - currently handles only one narrow multi-span special case well: compact interval headers
  - does not reconstruct generic multi-level header hierarchies
- `src/domain/assets/table_rows/table_row_canonicalizer.py`
  - is optimized for simple header/body, key-value, and schedule repairs
  - is not a generic span-aware table normalizer
- `src/domain/assets/table_rows/structured_row_renderer.py`
  - assumes “first row is the header” unless it detects a schedule matrix
  - flattens table meaning into text lines too early
- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
  - currently relies mostly on a flat row model plus type-specific fixes
  - works for spare parts and simple schedules
  - is not yet able to interpret performance curves, deeply nested spec tables, or multi-axis matrices generically

### Concrete observed failure

In:

- `outputs/debug_tables/PURO_30-OWNERS_MANUAL-HM13378-ROS213_table_assets.md`

This table is structurally a performance/curve matrix:

- pump identity row
- motor power columns
- a flow axis
- a head axis
- repeated numeric series

But the current structured text becomes:

- `Motor power=kW`
- `Q m3/h=Q l/min`
- `0=228`

That is not retrieval-grade or answer-generation-grade table understanding.

---

## Upgrade Goals

1. Preserve raw Docling extraction as the source of truth.
2. Add a span-aware normalization layer after Docling, not a document-specific repair layer.
3. Separate:
   - table category: spare parts, maintenance, technical data, troubleshooting, TOC
   - table shape: key-value, record table, schedule matrix, curve matrix, hierarchical spec matrix
4. Project normalized tables into typed structures before QA and extraction.
5. Keep Markdown as a human-readable fallback, not the primary machine representation.
6. Add selective fallback structure recovery only for low-quality tables, not for every table.

---

## Design Principles

- One file, one responsibility.
- No new flat folders.
- No document-specific value rules.
- No hardcoded current-database assumptions.
- Prefer additive metadata first, then tighten downstream consumers.
- Keep persisted raw table data intact even when new normalized projections are added.

---

## Proposed Package Layout

### 1. Parsing table structure normalization

Add:

- `src/application/workflows/parsing/tables/structure/__init__.py`
- `src/application/workflows/parsing/tables/structure/table_shape.py`
- `src/application/workflows/parsing/tables/structure/table_axis_role.py`
- `src/application/workflows/parsing/tables/structure/normalized_table_cell.py`
- `src/application/workflows/parsing/tables/structure/normalized_table_header.py`
- `src/application/workflows/parsing/tables/structure/normalized_table_row.py`
- `src/application/workflows/parsing/tables/structure/normalized_table.py`
- `src/application/workflows/parsing/tables/structure/span_grid_materializer.py`
- `src/application/workflows/parsing/tables/structure/header_band_detector.py`
- `src/application/workflows/parsing/tables/structure/header_path_builder.py`
- `src/application/workflows/parsing/tables/structure/unit_row_detector.py`
- `src/application/workflows/parsing/tables/structure/axis_role_inferer.py`
- `src/application/workflows/parsing/tables/structure/table_shape_classifier.py`
- `src/application/workflows/parsing/tables/structure/table_structure_quality_evaluator.py`
- `src/application/workflows/parsing/tables/structure/table_structure_normalizer.py`
- `src/application/workflows/parsing/tables/structure/table_structure_summary_serializer.py`

### 2. QA/extraction table projections

Add:

- `src/application/workflows/question_answering/answer_context/tables/projections/__init__.py`
- `src/application/workflows/question_answering/answer_context/tables/projections/projection_router.py`
- `src/application/workflows/question_answering/answer_context/tables/projections/record_table_projector.py`
- `src/application/workflows/question_answering/answer_context/tables/projections/schedule_matrix_projector.py`
- `src/application/workflows/question_answering/answer_context/tables/projections/performance_curve_projector.py`
- `src/application/workflows/question_answering/answer_context/tables/projections/specification_matrix_projector.py`
- `src/application/workflows/question_answering/answer_context/tables/projections/spare_parts_table_projector.py`
- `src/application/workflows/question_answering/answer_context/tables/projections/troubleshooting_table_projector.py`

### 3. Optional selective fallback structure recovery

Only after internal normalization is stable:

- `src/application/contracts/parsing/table_structure_provider.py`
- `src/infrastructure/parsing/tables/__init__.py`
- `src/infrastructure/parsing/tables/noop_table_structure_provider.py`
- `src/infrastructure/parsing/tables/paddle_table_structure_provider.py`
- `src/application/workflows/parsing/tables/fallback/__init__.py`
- `src/application/workflows/parsing/tables/fallback/low_quality_table_selector.py`
- `src/application/workflows/parsing/tables/fallback/selective_table_structure_recovery.py`

---

## Exact Existing Files To Change

### Parsing and normalization

- `src/config/settings/docling_settings.py`
- `src/infrastructure/parsing/docling/docling_converter_factory.py`
- `src/application/workflows/parsing/normalizers/docling_table_extractor.py`
- `src/application/workflows/parsing/normalizers/docling_table_row_grid_builder.py`
- `src/application/workflows/parsing/normalizers/docling_table_row_repairer.py`
- `src/application/workflows/parsing/normalizers/docling_document_normalizer.py`
- `src/application/workflows/parsing/builders/document_graph/parsed_asset_factory.py`
- `src/application/workflows/parsing/builders/document_graph/asset_metadata_synchronizer.py`
- `src/application/workflows/parsing/tables/table_semantic_resolver.py`
- `src/application/workflows/parsing/tables/logical_table_family_resolver.py`
- `src/application/workflows/parsing/tables/table_header_signature_builder.py`
- `src/application/workflows/parsing/tables/table_header_compatibility_matcher.py`
- `src/application/workflows/parsing/tables/semantics/table_semantic_classifier.py`
- `src/application/workflows/parsing/tables/semantics/table_matrix_detector.py`
- `src/application/workflows/parsing/tables/semantics/table_semantic_rule_evaluator.py`
- `src/application/workflows/parsing/tables/semantics/table_structured_list_classifier.py`

### Domain/raw row rendering

- `src/domain/assets/table_asset.py`
- `src/domain/assets/table_rows/table_row_canonicalizer.py`
- `src/domain/assets/table_rows/structured_row_renderer.py`
- `src/domain/assets/table_rows/table_row_patterns.py`

### Chunking and hydration

- `src/application/workflows/parsing/builders/chunking/builders/fragment/table_fragment_builder.py`
- `src/application/workflows/parsing/builders/chunking/builders/fragment/logical_table_family_fragment_builder.py`
- `src/application/workflows/parsing/builders/chunking/builders/chunk_payload_factory.py`
- `src/application/workflows/parsing/builders/document_graph/graph_chunk_builder.py`
- `src/application/workflows/extraction/batching/extraction_table_chunk_hydrator.py`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`

### QA projection and prompting

- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_schema_inferer.py`
- `src/application/services/answer_generation/formatting/structured_grid_row_parser.py`
- `src/application/services/answer_generation/formatting/spare_parts_table_parser.py`
- `src/application/services/ai/chunk_enrichment/markdown_table_metadata_extractor.py`

### Debug/reporting scripts

- `scripts/export_document_table_assets.py`
- `scripts/debug_answer_pipeline.py`
- `scripts/debug_parse_document.py`

---

## Phase Plan

## Phase 1 — Expose and preserve richer Docling table structure

Status: completed

### Goal

Make sure the parser and persisted table asset carry the best raw structure the current stack can provide before adding new semantics.

### Changes

- Add settings to `src/config/settings/docling_settings.py`:
  - `DOCLING_TABLE_STRUCTURE_MODE`
  - `DOCLING_TABLE_CELL_MATCHING`
- Wire them in `src/infrastructure/parsing/docling/docling_converter_factory.py`
  - use `pipeline_options.table_structure_options.mode`
  - use `pipeline_options.table_structure_options.do_cell_matching`
- Keep `ACCURATE` as the production default.
- Extend `src/application/workflows/parsing/normalizers/docling_table_extractor.py`
  - preserve any structure metadata that can be derived from spans without interpretation
- Extend `src/application/workflows/parsing/builders/document_graph/parsed_asset_factory.py`
  - keep `cell_spans` and raw row ids stable

### Tests

- Add/extend tests validating Docling converter settings wiring.
- Add tests proving table spans survive normalization/build unchanged.

---

## Phase 2 — Build a span-aware normalized table model

Status: partially implemented

Implemented so far:

- reusable structure-summary package scaffold under:
  - `src/application/workflows/parsing/tables/structure/`
- implemented normalized shape summaries for:
  - `maintenance_schedule_matrix`
  - `performance_curve_matrix`
- persisted:
  - `table_structure_quality`
  - `table_header_paths_json`
  - `table_axis_summary`

Not implemented yet:

- generic span grid materialization for arbitrary merged and multi-band headers
- general header-band detection
- generic header-path builder independent of current known shapes
- generic structure quality evaluator for all table families

### Goal

Stop treating all tables as flat header/body grids.

### Changes

Implement `src/application/workflows/parsing/tables/structure/`:

- `span_grid_materializer.py`
  - constructs a canonical span matrix from raw Docling spans
- `header_band_detector.py`
  - finds top header bands, side header bands, and title/unit rows
- `header_path_builder.py`
  - builds hierarchical header paths, e.g. `Motor power > kW`
- `unit_row_detector.py`
  - separates unit rows from semantic header rows
- `axis_role_inferer.py`
  - infers row axis, column axis, value axis, descriptor axis
- `table_shape_classifier.py`
  - classifies shape independent of category
- `table_structure_normalizer.py`
  - orchestrates the above and returns a `normalized_table`
- `table_structure_quality_evaluator.py`
  - scores whether the normalized table is reliable enough for downstream use

### Why this matters

This is the phase that fixes PURO-like failures generically.

### Tests

- multi-row header with units
- merged top headers
- merged left descriptor cells
- performance curve matrix
- maintenance matrix
- continuation table preserving header hierarchy

---

## Phase 3 — Separate table category from table shape

Status: partially implemented

Implemented so far:

- `table_shape` is now persisted separately from `table_category`
- current shape persistence covers the shapes detected by the structure-summary layer
- document metadata now includes `table_shape_counts`

Still remaining:

- shape inference beyond the currently supported matrices
- using normalized header paths in logical family matching
- broader shape-specific routing downstream

### Goal

Keep current semantic table categories, but enrich them with structural shape so downstream logic can behave correctly.

### Changes

- Keep `table_category` in:
  - `table_semantic_classifier.py`
  - `table_semantic_resolver.py`
- Add shape inference via the new structure package.
- Extend persisted metadata with:
  - `table_shape`
  - `table_structure_quality`
  - `table_axis_summary`
  - `table_header_paths_json`
- Update:
  - `table_header_signature_builder.py`
  - `table_header_compatibility_matcher.py`
  - to compare normalized header paths, not only flat first-row signatures

### Tests

- same category, different shape
- same shape, different category
- continued family matching with normalized header paths

---

## Phase 4 — Make chunking and hydration carry normalized table meaning

Status: not started

### Goal

Ensure the full table family that reaches extraction and QA includes normalized structure, not just Markdown plus raw rows.

### Changes

- Update `table_fragment_builder.py` and `logical_table_family_fragment_builder.py`
  - carry shape/category/quality metadata
- Update `chunk_payload_factory.py` and `graph_chunk_builder.py`
  - preserve shape-aware metadata on chunk payloads
- Update `extraction_table_chunk_hydrator.py`
  - append normalized table projection text or JSON payload
- Update `table_evidence_hydrator.py`
  - add normalized table payload metadata alongside `table_rows_json`

### Tests

- hydrated table chunk includes logical family rows and shape metadata
- retrieval QA hydration keeps full family plus normalized structure

---

## Phase 5 — Replace flat QA projection with typed table projections

Status: partially implemented

Implemented so far:

- `performance_curve_matrix` reaches QA as a typed table kind instead of flattening to weak pseudo facts

Still remaining:

- dedicated projector subpackage split by table kind
- maintenance, specification, and troubleshooting typed projector separation
- prompt-facing serialization based on typed projections rather than mixed row heuristics

### Goal

Make answer generation consume typed table semantics, not flattened row text.

### Changes

Implement `src/application/workflows/question_answering/answer_context/tables/projections/`:

- `record_table_projector.py`
  - generic structured records
- `schedule_matrix_projector.py`
  - maintenance/lubrication/schedule tables
- `performance_curve_projector.py`
  - flow/head/performance curve tables
- `specification_matrix_projector.py`
  - dimensional/spec matrices
- `spare_parts_table_projector.py`
  - richer spare parts projection than raw row parsing
- `troubleshooting_table_projector.py`
  - symptom/cause/remedy tables
- `projection_router.py`
  - selects the correct projector from category + shape

Then update:

- `answer_table_projector.py`
- `answer_table_schema_inferer.py`
- `structured_row_renderer.py`
- `structured_grid_row_parser.py`

### Tests

- PURO-like performance curve table becomes typed points, not `0=228`
- maintenance table becomes task + intervals + notes
- troubleshooting table becomes symptom/cause/remedy records
- technical data table becomes key-value/spec records only when structurally valid

---

## Phase 6 — Improve extraction to use normalized table evidence

Status: not started

### Goal

Extraction should benefit from the same structure improvements as QA.

### Changes

- Update `extraction_table_chunk_hydrator.py`
  - provide normalized table evidence payload per hydrated family
- Add extraction-side serializers if needed under:
  - `src/application/workflows/extraction/batching/`
- Keep raw markdown in the payload as fallback, but lead with normalized semantics

### Tests

- extraction sees complete table family
- extraction prompt contains normalized schedule/spec/parts semantics
- no regression for non-table chunks

---

## Phase 7 — Add selective low-quality table fallback

Status: not started

### Goal

Use a second table-structure engine only when Docling output is structurally weak.

### Changes

Add:

- `src/application/contracts/parsing/table_structure_provider.py`
- `src/infrastructure/parsing/tables/noop_table_structure_provider.py`
- `src/infrastructure/parsing/tables/paddle_table_structure_provider.py`
- `src/application/workflows/parsing/tables/fallback/low_quality_table_selector.py`
- `src/application/workflows/parsing/tables/fallback/selective_table_structure_recovery.py`

Possible triggers:

- too many repeated headers
- high merged-span ambiguity
- mostly numeric matrix with weak axis assignment
- row count high but header quality low
- markdown good but normalized structure confidence low

### Important rule

This fallback should run on cropped table images only, not whole pages or whole documents.

### Tests

- fallback not invoked on good Docling tables
- fallback invoked on low-quality tables
- fallback result improves normalized structure quality score

---

## Debug Output Upgrades

These should be added as each phase lands so the table pipeline stays inspectable.

### Update `scripts/export_document_table_assets.py`

Show:

- `table_shape`
- `table_structure_quality`
- `header_paths`
- `axis_roles`
- normalized structured projection preview
- fallback used or not

### Update `scripts/debug_answer_pipeline.py`

Show:

- raw hydrated rows
- normalized table shape
- typed projection
- prompt-facing serialized table payload

### Update `scripts/debug_parse_document.py`

Show:

- per-table normalization diagnostics
- low-confidence tables
- fallback candidates

---

## Recommended Implementation Order

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5
6. Phase 6
7. Phase 7

This order avoids patching QA/output first while the parser is still producing weak structure.

---

## Acceptance Criteria

### Parser/structure

- Multi-level headers are preserved as header paths.
- Merged cells are represented structurally, not flattened away.
- Table continuation across pages preserves one semantic table family.

### QA and retrieval

- The PURO performance table no longer projects to `0=228` style pseudo facts.
- Spare-parts tables remain strong after the structural upgrade.
- Maintenance matrices keep interval semantics.
- Technical/manual/datasheet tables are easier to retrieve because typed table evidence is cleaner.

### Architecture

- No new dump files.
- New logic grouped under existing parsing/QA table packages.
- Fallback library use is selective and optional.
- Debug scripts expose structure quality and typed projections clearly.

---

## First Implementation Slice

The safest first slice is:

1. Phase 1 wiring for Docling table structure settings
2. Phase 2 span-aware normalization skeleton
3. one end-to-end typed shape:
   - `performance_curve_matrix`

Why:

- it targets the exact currently observed weakness
- it is generic across manuals and datasheets
- it proves the architecture before expanding to other table types

After that, the next best slice is:

- `maintenance_schedule_matrix`
- then `specification_matrix`
- then selective fallback

### Next active slice

1. strengthen `maintenance_schedule_matrix` with richer header-path and axis metadata in chunk hydration and answer/debug output
2. add `specification_matrix` / technical-grid shape support
3. feed the richer normalized payload into QA and extraction before introducing fallback engines
