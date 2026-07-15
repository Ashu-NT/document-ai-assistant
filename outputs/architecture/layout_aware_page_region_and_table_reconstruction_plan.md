# Layout-Aware Page Region And Table Reconstruction Plan

## Executive Summary

The core gap is no longer basic table detection.

Your codebase already does a lot well:

- Docling tables are extracted into Markdown, rows, spans, and dimensions.
- Logical table families are resolved across continued tables.
- Table category, shape, header paths, and axis summaries are already propagated.
- QA and extraction already hydrate full table families and already consume structured table metadata.

The weak point is earlier in the parsing stack:

- page content is still flattened too early
- same-page parallel structures are not modeled as separate visual regions
- TOC reconstruction is still row-based instead of page-region-based
- logical family resolution still assumes a mostly linear page stream

That is why issues like these still appear:

- dual-column TOC pages split or misread
- left/right tables on the same page can bleed into one another
- section-path quality degrades because table structure is reconstructed after layout meaning is already lost
- downstream answer generation receives structured tables, but only after a weaker reconstruction stage

The right direction is:

`page -> layout regions -> region-local reading order -> region-local table/TOC reconstruction -> logical family merge if justified`

not:

`page -> flatten page -> reconstruct one grid -> try to repair downstream`

This plan keeps the current architecture, avoids dump files, and uses the existing persistence and hydration seams already present in the repo.

---

## Scope

This plan is specifically about:

- page-layout awareness
- multi-column and parallel-stream handling
- TOC reconstruction quality
- same-page table separation
- region-aware logical table continuation
- propagation of layout metadata through parsing, persistence, retrieval, and answer preparation

This plan complements but does not replace:

- `outputs/architecture/table_structure_enterprise_upgrade_plan.md`
- `outputs/architecture/table_handling_enterprise_standard_audit.md`
- `outputs/architecture/parsing_chunking_document_understanding_upgrade_plan.md`

Those documents cover table structure, table semantics, and broader parsing/chunking strategy.
This document fills the specific missing layer:

- layout-aware page segmentation and reconstruction

## Anti-Overfitting Guardrail

The benchmark/debug documents in the DB are evidence samples, not rule sources.

That distinction now needs to be explicit.

The current codebase is not mainly hardcoded to exact document names like
`FWC12`, `PURO`, or one specific manual title. However, a deeper scan shows a
different risk:

- many parsing and table decisions are still driven by fixed marker lists
- each new document miss can tempt the system toward "just add one more phrase"
- that creates sample-shaped tuning even when the code is not literally
  document-name-specific

This plan must therefore enforce the following rule:

- no new parsing/table rule may be justified only because it fixes one current
  DB document

Approved rule sources:

- layout structure
- page-region structure
- table geometry
- span and continuation behavior
- section numbering / hierarchy behavior
- generic engineering-document archetypes
- generic semantic signals that are valid across many technical documents

Disallowed direction:

- patching classification or reconstruction because one current document uses a
  convenient phrase such as `Card of Task Specification`, `List of tools`, or
  another corpus-local wording

The correct target is enterprise-safe generalization:

- unseen manuals
- unseen datasheets
- unseen certificates
- unseen reports
- unseen drawings

must benefit because the system understands document archetypes and structure,
not because their wording happened to resemble the current DB.

## Generic-First Decision Stack

Future work under this plan should follow this ranking of evidence strength:

1. page layout and region separation
2. table geometry and span/continuation behavior
3. row/column role inference
4. generic table archetype detection
5. semantic arbitration across competing interpretations
6. lexical markers as supporting evidence only

This is important because the current weak spot is not lack of markers. It is
that markers are often doing work that should be owned by structure and
archetype detection.

## Current Overfitting Risk Hotspots

The deeper scan shows that the following files are the main places where
sample-shaped tuning could creep in if future work is not disciplined:

- `src/application/workflows/parsing/tables/semantics/table_semantic_classifier.py`
- `src/application/workflows/parsing/tables/semantics/table_semantic_rule_evaluator.py`
- `src/application/workflows/parsing/tables/semantics/table_specification_rule_evaluator.py`
- `src/application/workflows/parsing/tables/semantics/table_structured_list_classifier.py`
- `src/domain/assets/table_rows/table_row_patterns.py`
- `src/domain/assets/table_rows/compact_schedule_matrix_canonicalizer.py`
- `src/domain/assets/table_rows/spare_parts_table_normalizer.py`
- `src/domain/assets/table_rows/troubleshooting_table_normalizer.py`
- `src/application/prompts/answer_generation/prompt_context/tables/prompt_table_type_detector.py`

These are not "bad" files. Several of them are useful and already moving in the
right direction. The risk is that they are still mostly marker/phrase-driven.

So the next architecture step should not be:

- add more marker lists first

It should be:

- introduce stronger archetype and structure layers first, then let markers act
  as bounded supporting signals

## Evidence Update From `sdt_1_Betriebsanleitung_EN_table_assets.md`

The latest exported table-asset report confirms that the original direction is correct, but it also exposes a few additional concrete requirements that need to be part of the plan.

### A. TOC is still being persisted as a generic record-style table too early

Observed symptoms:

- the TOC family is correctly detected as `toc_table`
- but its stored section path is still a noisy pre-body value:
  - `Â© SCHIFFSDIESELTECHNIK KIEL GmbH`
- its persisted `header_paths` still look like flattened TOC fragments rather than a true outline model
- its structured rows still degrade into `header=value` style lines instead of clean outline entries

Implication:

- region-aware reconstruction alone is not enough
- the TOC path also needs:
  - pre-body section-path suppression
  - an outline-first persisted representation
  - special handling so `toc_table` does not fall back to generic record-table projection

### B. Section-path hygiene must start before normal body hierarchy is trusted

Observed symptoms:

- TOC tables are anchored under copyright/preamble text instead of a neutral pre-body area
- this means section ownership is still being assigned too early for front-matter layout-heavy pages

Implication:

- the plan must explicitly include a pre-body / front-matter gate
- front-matter regions must not donate persisted section paths to TOC and similar structural tables

### C. Semantic category arbitration still needs a stronger second pass

Observed symptoms:

- a technical-data family under `3 Technical data > Operating fluid systems` is categorized as `spare_parts_table`
- many legitimate manual tables still fall back to `general_table`

Implication:

- once region-aware reconstruction is in place, table category resolution still needs a semantic arbitration pass that weighs:
  - section semantics
  - header semantics
  - units / values / engineering signal density
  - row archetype
  - nearby text
- category decisions should not overreact to one local lexical cue

### D. Text normalization is still leaking mojibake into persisted assets

Observed symptoms in the export:

- `Â©`
- `Â°C`
- bullet corruption such as `âˆ™`
- smart-quote corruption in some table lines

Implication:

- the plan must include a text-normalization hardening slice at canonical normalization time
- otherwise even correct structure is degraded before retrieval, extraction, and answer generation

### E. TOC, legend, glossary, and qualification tables need clearer non-record roles

Observed symptoms:

- some front-matter/manual support tables remain `general_table`
- the current representation is still biased toward `record_table` even when the table is really:
  - TOC / outline
  - symbol legend
  - glossary / abbreviation list
  - qualification / responsibility matrix

Implication:

- the plan should explicitly separate:
  - visual reconstruction
  - semantic role detection
  - projection strategy

## Evidence Update From `OMM_maintenance-14483_table_assets.md`

This second export exposes a different but equally important failure family. It is not primarily a TOC problem. It is a template-heavy maintenance-manual problem.

### F. Repeated task-card templates are being flattened into generic record tables

Observed symptoms:

- almost every family is still `general_table`
- many tables are clearly not generic tables at all
- the document is dominated by repeated maintenance task cards with fields such as:
  - `Location`
  - `Description of Task`
  - `Service No.`
  - `Description of required resources`
  - numbered checklist/procedure lines

Implication:

- the plan needs an explicit semantic family for maintenance task-card / job-card / work-card style tables
- these should not be forced through the same projection path as ordinary key-value record tables

### G. Visually repeated columns are being preserved as duplicated evidence instead of collapsed into one canonical form

Observed symptoms:

- many tables repeat the same textual column payload across 3-5 columns
- examples show:
  - `Card of Task Specification` repeated across columns
  - `Description of required resources` repeated across columns
  - the same caution/procedure text duplicated in parallel columns

Implication:

- region-aware layout is necessary, but not sufficient
- the plan also needs a generic repeated-column collapse stage for template forms
- this collapse must be structural and similarity-based, not document-specific

### H. Hierarchical task-card rows are being flattened into weak `label=value` lines

Observed symptoms:

- numbered procedural rows become:
  - `Card of Task Specification=1.`
  - `Card of Task Specification=2.`
  - `Description of Task:=4.`
- real semantics are being lost:
  - personnel requirement
  - consumables
  - safety cautions
  - step-by-step procedure
  - image/reference block
  - additional manual note

Implication:

- the plan must treat these as hierarchical form sections, not just table rows
- row reconstruction needs a typed field/value extraction layer for task-card templates

### I. Row continuation and subordinate text blocks are not being attached to the owning row correctly

Observed symptoms:

- in at least one table, a safety instruction line follows the main numbered row but is effectively detached from the owning caution section
- long procedure rows remain one large block instead of:
  - procedure heading
  - ordered/bulleted task steps
  - attached caution/attention note

Implication:

- the plan needs a generic row-attachment / continuation merger
- this should attach subordinate lines to the nearest compatible owning row by structure and indentation, not by hardcoded phrases

### J. Section-path recursion and template-title repetition are now a first-class gap

Observed symptoms:

- persisted paths such as:
  - `Maintenance Instructions Marine Lift 14483 (Crew Lift)`
  - `Maintenance Instructions Marine Lift 14483 (Crew Lift) > Card of Task Specification > Maintenance Instructions Marine Lift 14483 (Crew Lift)`
  - `Maintenance Instructions Marine Lift 14483 (Crew Lift) > Card of Task Specification > Maintenance Instructions Marine Lift 14483 (Crew Lift) > Card of Task Specification`

Implication:

- section-path hygiene is not only about front matter
- the plan must also include loop/repetition suppression for template-derived section paths
- stored section paths should prefer stable semantic anchors over repeated page-template headings

### K. Maintenance-manual tables need dedicated support-table roles

Observed symptoms:

- `List of tools` is treated as `general_table`
- task cards, resource cards, and checklist-like cards are also treated as `general_table`

Implication:

- the plan needs support for reusable generic roles such as:
  - tool list
  - maintenance task card
  - resource requirement card
  - safety instruction card
  - procedure checklist

These are still generic enterprise document patterns, not document-specific rules.

### L. Text repair still needs to normalize extracted bullets and broken word joins inside procedure content

Observed symptoms:

- bullets such as `â€¢`
- broken line-join artifacts like `assem blies`
- other OCR/text-extraction join issues inside long procedure cells

Implication:

- text normalization must include:
  - bullet repair
  - soft line-break / control-character cleanup
  - word rejoin cleanup for split tokens inside long table cells

## Repo Scan Coverage

The scan for this plan covered the code paths that actually influence:

- Docling normalization
- TOC detection and reconstruction
- table extraction and logical family resolution
- document graph build and persistence
- table hydration for extraction and QA
- prompt-context table projection
- table debug/export scripts

Key areas reviewed:

- `src/application/workflows/parsing/*`
- `src/application/workflows/question_answering/*`
- `src/application/workflows/extraction/*`
- `src/application/prompts/answer_generation/*`
- `src/infrastructure/db/mappers/document/*`
- `src/infrastructure/db/repositories/document/*`
- `scripts/debug_parse_document.py`
- `scripts/export_document_table_assets.py`

---

## Codebase Findings

### 1. Canonical normalization already captures geometry, but not layout regions

Current seams:

- `src/application/workflows/parsing/normalizers/docling_document_normalizer.py`
- `src/domain/common/source_location.py`

Observed behavior:

- `DoclingDocumentNormalizer.normalize()` already builds canonical elements with:
  - `page_start`
  - `page_end`
  - `bbox`
  - `section_path`
- `_build_metadata()` already stores:
  - `markdown`
  - `table_rows`
  - `table_cell_spans`
  - `row_count`
  - `column_count`

Missing:

- page orientation
- layout region identity
- lane / column identity
- page-local reading order inside separate regions
- region role such as TOC stream vs table region vs side note
- front-matter / pre-body gating so early structural pages do not inherit noisy section ownership
- stronger mojibake cleanup before metadata is persisted

### 2. Table extraction is still grid-first, not layout-first

Current seams:

- `src/application/workflows/parsing/normalizers/docling_table_extractor.py`
- `src/application/workflows/parsing/normalizers/docling_table_row_grid_builder.py`

Observed behavior:

- `DoclingTableExtractor.extract_rows()` delegates to `DoclingTableRowGridBuilder`
- `DoclingTableExtractor.extract_cell_spans()` preserves row/column spans
- `DoclingTableExtractor.extract_dimensions()` measures the raw Docling cell grid

Missing:

- region-aware partitioning before row-grid construction
- separate handling for parallel streams on the same page
- layout-aware reconstruction for multi-column TOC and side-by-side tables

### 3. TOC reconstruction is row-aware, but not page-region-aware

Current seams:

- `src/application/workflows/parsing/normalizers/docling_toc_table_row_reconstructor.py`
- `src/application/workflows/parsing/builders/section_hierarchy/toc/toc_candidate_collector.py`
- `src/application/workflows/parsing/builders/section_hierarchy/toc/toc_entry_parser.py`

Observed behavior:

- TOC handling already has dedicated reconstruction and parsing logic
- `TocEntryParser` can parse TOC rows and TOC text
- `TocCandidateCollector` can chain TOC candidate elements across pages

Missing:

- explicit separation of left-column and right-column TOC streams
- region-aware ordering before row parsing
- better handling of wrapped TOC entries inside one visual region
- outline-first persistence for `toc_table` instead of generic record-style projection
- suppression of pre-body section-path contamination for TOC pages

### 4. Page size is already available, but not fully exploited

Current seam:

- `src/application/workflows/parsing/builders/document_graph/page_size_extractor.py`

Observed behavior:

- `PageSizeExtractor.extract()` already reads `(width, height)` per page from Docling output
- page sizes already flow into chunking/runtime paths

Missing:

- explicit orientation normalization
- region segmentation using page width / height
- a shared layout-analysis model built from those page sizes

### 5. Logical table continuation is still mostly linear

Current seam:

- `src/application/workflows/parsing/tables/logical_table_family_resolver.py`

Observed behavior:

- continuation checks already use:
  - section consistency
  - header compatibility
  - anchor compatibility
  - compatible column counts
  - page adjacency

Missing:

- protection against same-page cross-region continuation
- region-aware continuation scoring
- same-page continuation rules that distinguish:
  - true wrapped/continued table
  - unrelated table in another lane/region
- category-aware continuation sanity checks for cases where engineering data and spare-parts semantics conflict

### 6. Persistence seams are already strong enough

Current seams:

- `src/application/workflows/parsing/builders/document_graph/parsed_asset_factory.py`
- `src/infrastructure/db/repositories/document/document_graph_reader.py`
- `src/infrastructure/db/mappers/document/element_mapper.py`

Observed behavior:

- parser metadata is already round-tripped through `parser_extra`
- `ParsedAssetFactory` already hydrates structural table fields into `TableAsset`
- `DocumentGraphReader` already rebuilds `TableAsset` from persisted parser metadata

Implication:

- layout-aware metadata can be added without inventing a new storage architecture
- the existing `parser_extra -> element -> table asset -> graph -> chunk` path is the correct propagation route

### 7. Downstream consumers are already prepared to benefit

Current seams:

- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/extraction/batching/extraction_table_chunk_hydrator.py`
- `src/application/prompts/answer_generation/prompt_context/*`

Observed behavior:

- QA already hydrates full logical table families
- extraction already hydrates full table chunks
- prompt context already carries:
  - `table_rows`
  - `table_shape`
  - `table_structure_quality`
  - `table_header_paths`
  - `table_axis_summary`

Implication:

- better parsing and reconstruction quality will lift retrieval, extraction, and answering without redesigning those layers

### 8. File-size hygiene already needs to be protected

Current oversized files in this target area:

- `src/application/workflows/parsing/builders/document_graph_builder.py` — 339 LOC
- `scripts/export_document_table_assets.py` — 533 LOC

Implication:

- do not add more logic directly into these files
- any new work must go into dedicated collaborators and subfolders

### 9. The remaining gap is archetype depth, not more vocabulary

The deeper scan confirms that the table stack already has many useful semantic
families and normalizers:

- TOC / outline
- maintenance interval matrices
- troubleshooting tables
- spare-parts tables
- technical/specification tables
- certificate-oriented tables
- connection and identifier tables

That is good progress.

What is still missing is a stronger generic archetype layer that can unify
future documents without growing into a phrase-collection system.

The current architecture therefore needs to move toward stable document-table
archetypes such as:

- outline / TOC
- engineering record / specification matrix
- maintenance schedule matrix
- troubleshooting matrix
- spare-parts listing
- task / work card form
- checklist / procedure card
- tool / resource list
- legend / glossary / abbreviation list

This is the right level of abstraction for enterprise reuse.

---

## Architectural Decision

### Decision

Introduce a dedicated page-layout analysis layer inside parsing, then make TOC reconstruction and table reconstruction consume that layout model before semantic classification and logical-family resolution.

### Why this is the right abstraction

The problem is not just TOC.

The same missing abstraction affects:

- TOC pages
- same-page left/right tables
- tables on landscape pages
- pages mixing callouts, notes, and tables
- section assignment around visually parallel content

The missing concept is:

- visual region identity on a page

### What not to do

Do not solve this with:

- document-specific header lists
- more downstream row heuristics only
- hardcoded TOC-only rules
- hardcoded left/right split thresholds without a reusable layout model
- pandas as a primary parsing abstraction

Pandas can be helpful for debugging or analytics, but it is not the right core domain abstraction for enterprise parsing.

---

## Design Principles

1. Keep parsing deterministic.
2. Keep layout analysis separate from semantic classification.
3. Persist layout metadata through existing parser metadata seams.
4. Reconstruct per region first, then merge only when justified.
5. Keep TOC and table reconstruction region-aware, not doc-specific.
6. Do not expand already-large orchestration files.
7. No new dump files.
8. No file touched by this change should exceed 300 LOC.
9. Favor archetype-specific normalizers over global marker inflation.
10. Treat lexical markers as low-to-medium confidence signals, never as the
    primary source of truth when structure disagrees.

---

## Proposed Package Structure

### 1. Layout foundation

Create:

- `src/application/workflows/parsing/layout/__init__.py`
- `src/application/workflows/parsing/layout/models/__init__.py`
- `src/application/workflows/parsing/layout/models/page_layout_analysis.py`
- `src/application/workflows/parsing/layout/models/page_layout_region.py`
- `src/application/workflows/parsing/layout/models/layout_region_role.py`
- `src/application/workflows/parsing/layout/page_orientation_resolver.py`
- `src/application/workflows/parsing/layout/layout_lane_detector.py`
- `src/application/workflows/parsing/layout/layout_region_builder.py`
- `src/application/workflows/parsing/layout/layout_reading_order_resolver.py`
- `src/application/workflows/parsing/layout/page_layout_analyzer.py`
- `src/application/workflows/parsing/layout/layout_metadata_serializer.py`

Responsibilities:

- page orientation inference
- page lane/column detection
- region construction from element bbox clusters
- region-local reading order
- serialization of layout metadata into parser metadata

### 2. Region-aware reconstruction

Create:

- `src/application/workflows/parsing/tables/reconstruction/__init__.py`
- `src/application/workflows/parsing/tables/reconstruction/parallel_stream_detector.py`
- `src/application/workflows/parsing/tables/reconstruction/region_partition.py`
- `src/application/workflows/parsing/tables/reconstruction/region_aware_table_reconstructor.py`
- `src/application/workflows/parsing/tables/reconstruction/region_aware_toc_reconstructor.py`
- `src/application/workflows/parsing/tables/reconstruction/wrapped_row_merger.py`
- `src/application/workflows/parsing/tables/reconstruction/reconstruction_decision.py`

Responsibilities:

- partition Docling table cells by visual region
- reconstruct row grids within a region
- merge wrapped rows only within compatible local context
- reconstruct multi-column TOC from region streams instead of flattened rows

### 3. Optional TOC subfolder cleanup if touched

If TOC internals are modified materially, keep them grouped:

- `src/application/workflows/parsing/builders/section_hierarchy/toc/parsing/*`
- `src/application/workflows/parsing/builders/section_hierarchy/toc/collection/*`

This is optional, but if any file grows past 300 LOC it should be split there instead of enlarged in place.

---

## Metadata To Add

Add layout metadata to `parser_metadata.extra` for tables and any other affected canonical elements.

Recommended fields:

- `page_width`
- `page_height`
- `page_orientation`
- `layout_region_id`
- `layout_region_role`
- `layout_lane_index`
- `layout_lane_count`
- `layout_reading_order`
- `layout_region_bbox`
- `layout_model_version`

For table-specific reconstruction:

- `table_region_partition_version`
- `table_local_reading_order`
- `table_parallel_stream_index`
- `table_parallel_stream_total`

Important:

- Keep `SourceLocation` geometry-only in the first pass.
- Persist layout semantics in parser metadata first.
- Only widen domain location models later if real downstream need appears.

---

## Concrete Change Map

### Parsing / normalization

- `src/application/workflows/parsing/normalizers/docling_document_normalizer.py`
  - call page layout analysis
  - attach serialized layout metadata to canonical element metadata
  - keep current table extraction responsibilities light

- `src/application/workflows/parsing/normalizers/docling_table_extractor.py`
  - delegate region-aware reconstruction instead of only one flat row-grid path
  - keep markdown extraction separate from row reconstruction

- `src/application/workflows/parsing/normalizers/docling_table_row_grid_builder.py`
  - keep as low-level grid builder
  - do not turn it into a layout analyzer
  - only use it after partitioning cells per region

- `src/application/workflows/parsing/normalizers/docling_toc_table_row_reconstructor.py`
  - convert into a region-aware TOC row reconstructor or wrap it with one

### TOC / section hierarchy

- `src/application/workflows/parsing/builders/section_hierarchy/toc/toc_candidate_collector.py`
  - allow layout-aware TOC candidate acceptance

- `src/application/workflows/parsing/builders/section_hierarchy/toc/toc_entry_parser.py`
  - consume region-aware TOC rows
  - stop assuming one flattened row stream

### Table assets / graph build / persistence

- `src/application/workflows/parsing/builders/document_graph/parsed_asset_factory.py`
  - map layout metadata from parsed element metadata into `TableAsset.metadata` and related fields

- `src/infrastructure/db/repositories/document/document_graph_reader.py`
  - rehydrate layout metadata from persisted parser metadata

- `src/infrastructure/db/mappers/document/element_mapper.py`
  - ensure layout metadata persists round-trip if not already covered by parser-extra handling

### Logical family / semantics

- `src/application/workflows/parsing/tables/logical_table_family_resolver.py`
  - add region-aware continuation guards
  - avoid same-page cross-lane family merges

- `src/application/workflows/parsing/tables/table_semantic_resolver.py`
  - optionally consume region role and region-local structure confidence

- introduce an archetype-oriented layer in the table-semantics path so semantic
  roles are inferred from:
  - structure
  - spans
  - row archetypes
  - repeated field behavior
  - section numbering context
  before lexical fallback decides the category

- `src/application/prompts/answer_generation/prompt_context/tables/prompt_table_type_detector.py`
  - treat persisted metadata and archetype/category results as primary
  - use section-path or header-text lexical fallback only as a low-confidence
    backup, not as a silent override

### Debug / export / QA propagation

- `scripts/export_document_table_assets.py`
  - split if touched
  - expose layout metadata and region family info in report output

- `scripts/debug_parse_document.py`
  - expose page layout / region diagnostics in the debug report

- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
  - preserve layout-origin metadata when hydrating table evidence

- `src/application/workflows/extraction/batching/extraction_table_chunk_hydrator.py`
  - preserve region-aware ordering when hydrating structured table text

---

## Implementation Phases

## Implementation Progress Update

The following slices are now implemented in code:

- Phase 1 foundation:
  - page orientation detection
  - page lane detection
  - page-region assignment
  - layout metadata serialization into canonical element metadata
- Phase 4 guardrail slice:
  - same-page logical table family continuation now rejects incompatible layout lanes for non-TOC tables
- Phase 2 partial slice:
  - `TableCellSpan` now preserves optional per-cell page/bbox geometry when available
  - Docling table-cell normalization now canonicalizes geometry-aware spans once
  - TOC reconstruction now supports true multi-cell TOC rows, not only single flattened strings
  - a geometry-aware parallel TOC reconstructor now activates when per-cell geometry indicates separate page lanes and each lane independently reconstructs into a valid TOC stream
- Phase 3 partial slice:
  - same-page non-TOC tables can now be reconstructed as separate parallel streams when geometry shows distinct lanes and each lane forms a valid local table
  - repeated-header sibling tables no longer depend on sparse merged grids to be recognized as separate evidence streams
  - local lane row grids are rebased to stream-local row/column coordinates before repair, preventing right-hand tables from carrying leading empty columns
  - parallel-stream table metadata now persists through canonical metadata, table assets, DB rehydration, and extraction-time renderers
  - debug/structure renderers can now expose `parallel_stream_rows` plus local reading order for downstream inspection
- Phase 5 partial slice:
  - category-aware persisted row normalization now runs after table semantic classification
  - troubleshooting tables with wrapped cause/remedy rows are normalized into clean persisted `table_rows` before chunking and storage
  - spare-parts tables are normalized into canonical persisted row grids before downstream extraction and answer rendering
  - normalized main rows and normalized parallel-stream rows are written back into element parser metadata so DB rehydration and chunking consume the same upgraded structure
 - Phase 3 additional slice:
   - raw Docling row repair now includes generic adjacent duplicate-template column collapse before semantic classification
   - raw Docling row repair now includes generic sparse continuation-row attachment for subordinate wrapped text blocks that belong to the previous row
   - these structural repairs run at the shared parsing seam, so persistence, chunking, extraction, and QA all consume the same upgraded row grids

Still intentionally pending:

- richer region-aware wrapped-row / continuation merging driven by lane- or region-local context
- semantic/chunking alignment work that consumes the stronger reconstruction layer for more than TOC
- deeper repeated-column/template-form collapse for non-adjacent or partially shifted duplicate streams
- richer debug surfacing of stream-level quality and region-cluster diagnostics

## Phase 1 — Page Layout Metadata Foundation

Goal:

- build page-local layout understanding once
- keep it deterministic
- keep it independent of semantic table classification

Work:

- implement `PageLayoutAnalyzer`
- resolve page orientation from `PageSizeExtractor`
- detect page lanes from element bbox distributions
- assign each canonical element to a layout region
- serialize region metadata into canonical element metadata
- add front-matter / pre-body detection so early layout-heavy pages are marked separately from trusted body hierarchy
- harden text cleanup for mojibake before layout metadata and table metadata are persisted

Acceptance:

- every element with a page and bbox can optionally carry region metadata
- front-matter regions are explicitly identifiable
- obvious mojibake no longer survives into persisted table assets
- no behavioral change yet to QA/retrieval

## Phase 2 — Region-Aware TOC Reconstruction

Goal:

- stop treating dual-column TOC pages as one flattened row stream

Work:

- introduce region-local TOC extraction
- reconstruct TOC entries per visual region
- merge final TOC streams in proper page reading order
- preserve wrapped entries inside one local region
- persist TOC as an outline-first structure, not only as a generic record-table row grid
- prevent TOC tables from inheriting copyright/preamble section ownership

Acceptance:

- dual-column TOC pages produce coherent TOC entries
- TOC continuation across pages still works
- exported TOC families have neutral or TOC-specific structural ownership, not noisy front-matter section paths
- TOC structured output reads like outline entries instead of `header=value` artifacts

## Phase 3 — Region-Aware Table Reconstruction

Goal:

- reconstruct same-page tables from local visual regions first

Work:

- partition Docling table cells by region/lane
- build local row grids per region
- merge wrapped rows only within a compatible local stream
- preserve separate tables on the same page when they occupy different regions
- detect and collapse visually repeated parallel columns when they are template duplicates rather than independent evidence streams
- add generic continuation attachment for subordinate safety/procedure lines that belong to the owning row

Acceptance:

- same-page left/right tables no longer merge incorrectly
- wrapped rows improve without doc-specific rules
- repeated template columns no longer survive as duplicated evidence payloads

Status update:

- partially implemented
- completed in this slice:
  - region/lane-aware non-TOC parallel stream reconstruction
  - repeated-header side-by-side table recovery even when the merged Docling grid is dense
  - persistence and downstream hydration of parallel-stream table metadata
- still pending inside Phase 3:
  - richer region-local continuation attachment when duplicate streams are only partially aligned
  - deeper duplicate-stream collapse for non-adjacent or offset template columns
  - richer stream-level diagnostics for debug exports

## Phase 4 — Logical Family Resolver Upgrade

Goal:

- make family continuation aware of layout regions

Work:

- use layout region metadata in continuation checks
- forbid same-page continuation across incompatible regions
- allow true within-region continuation and compatible cross-page continuation

Acceptance:

- logical family grouping remains strong for real continuations
- false family merges drop materially

## Phase 5 - Semantic And Chunking Alignment

Goal:

- align section paths, table semantics, and chunk content with the improved reconstruction

Work:

- allow semantic classification to use cleaner region-local headers/rows
- prevent section-path contamination from parallel unrelated page content
- ensure chunk building receives improved table assets and cleaner section context
- add an explicit generic table-archetype inference layer so the system can
  distinguish:
  - outline / TOC
  - engineering specification matrix
  - maintenance schedule matrix
  - troubleshooting matrix
  - spare-parts list

Status update:

- partially implemented
- completed in this slice:
  - category-aware persisted row normalization for troubleshooting and spare-parts tables
  - propagation of normalized rows back into parser metadata for storage, rehydration, and chunking
  - generic raw-row structural cleanup for duplicated template columns and sparse subordinate continuation rows
- still pending inside Phase 5:
  - broader chunking/ranking adaptations that explicitly consume the cleaner normalized row structures
  - stronger region-aware continuation attachment driven by lane-local structure
  - task/work card
  - checklist/procedure card
  - tool/resource list
  - legend/glossary list
- add category arbitration so engineering/specification tables are not over-promoted into `spare_parts_table`
- distinguish support-table roles such as:
  - legend / symbol table
  - glossary / abbreviation table
  - qualification / responsibility table
  - TOC / outline table
- add generic maintenance-manual support roles such as:
  - maintenance task card
  - procedure checklist
  - resource requirement card
  - tool list
  - safety instruction card
- suppress recursive/repeated section paths caused by page-template headings
- project hierarchical task-card rows into typed field/value sections instead of weak `header=value` record rows

Acceptance:

- table category and chunk typing improve indirectly from better source structure
- TOC and table chunks no longer inherit as much noisy path context
- technical-data tables stop drifting into unrelated semantic categories because of one weak lexical signal
- maintenance task-card tables stop collapsing into indistinguishable `general_table` record payloads
- unseen documents benefit because they match stable archetypes and structure,
  not because their wording was already seen in the current DB corpus

## Phase 6 — Persistence And Debug Surfaces

Goal:

- make new layout semantics inspectable and durable

Work:

- round-trip layout metadata through persistence
- update debug parsing report
- update table export report
- add explicit debug display for:
  - region id
  - lane index/count
  - orientation
  - region role

Acceptance:

- you can inspect region-aware reconstruction without guessing from raw markdown

## Phase 7 — QA / Extraction / Prompt Propagation

Goal:

- let downstream systems benefit from improved structure without redesign

Work:

- keep table hydration family-aware and region-aware
- preserve local row order in hydrated content
- expose layout metadata to prompt context where useful

Acceptance:

- answer generation sees better table evidence because parsing is better
- no new ad-hoc prompt hacks are needed for basic table coherence

---

## Test Plan

### Unit tests

Add or extend tests for:

- page orientation inference from page sizes
- dual-column page lane detection
- region assignment from bbox clusters
- dual-column TOC reconstruction
- same-page left/right table separation
- landscape page table reconstruction
- wrapped-row continuation within a region
- prevention of wrapped-row continuation across unrelated regions
- logical family resolver rejecting same-page cross-region continuation
- persistence round-trip of layout metadata
- archetype inference staying correct when wording changes but layout/structure
  stays equivalent
- prevention of corpus-shaped regressions where one extra marker would change a
  table type without enough structural support

### Integration tests

Add integration-style tests for:

- `DoclingDocumentNormalizer -> ParsedAssetFactory -> DocumentGraphReader`
- `TableEvidenceHydrator` consuming region-aware table assets
- extraction table hydration preserving family and row order

### Script/debug verification

Verify with:

- `scripts/debug_parse_document.py`
- `scripts/export_document_table_assets.py`

Expected verification:

- region metadata is visible
- TOC pages are represented as structured outline streams
- left/right same-page tables appear as distinct table assets unless a merge is justified

---

## Performance Strategy

This upgrade must stay efficient.

Rules:

- analyze page layout once per page, not once per downstream consumer
- compute regions from bbox clustering and page width/height, not heavy model inference
- keep reconstruction deterministic and linear or near-linear in element count per page
- store layout metadata once and reuse it downstream

Avoid:

- repeated per-consumer re-analysis of page layout
- heavy fallback OCR or additional external models for this layer
- DataFrame-first processing in core parsing

---

## Refactor / File-Size Rules

Mandatory implementation rule set:

- no new file may exceed 300 LOC
- no touched file may be allowed to drift upward if it is already oversized
- if `DocumentGraphBuilder` needs new responsibilities, extract collaborators instead
- if `scripts/export_document_table_assets.py` is touched, split it into helper modules under a grouped script-support package
- keep subfolders grouped by responsibility, not flat

---

## Non-Goals

This plan does not do these things:

- replace Docling
- replace your current chunking architecture with Docling HybridChunker
- introduce LLM-based table parsing
- add doc-specific rules for one manual or one truth-set family
- add new semantic rules only because they fix one current debug/DB document
- use pandas as the core table domain model

It can still use:

- generic engineering-table signals
- generic outline/TOC signals
- generic front-matter detection
- generic unit/value density signals

Those are document-agnostic and are compatible with enterprise maintainability.

---

## Acceptance Criteria

This plan is considered fully implemented when:

- page-local layout regions exist as a first-class parsing concept
- TOC reconstruction is region-aware
- same-page left/right tables do not get flattened into one stream
- landscape pages are normalized correctly
- logical table continuation uses region-aware guards
- layout metadata persists and rehydrates cleanly
- debug/export scripts show layout metadata explicitly
- downstream QA/extraction consume the stronger structure without ad-hoc hacks
- prompt-time table typing depends primarily on persisted structure/archetype
  metadata rather than fragile lexical fallback
- a new technical document can classify/project core table families correctly
  without needing a corpus-specific phrase patch
- no new dump files are introduced
- no touched file exceeds 300 LOC

---

## Recommended Implementation Order

1. Phase 1 — page layout metadata foundation
2. Phase 2 — region-aware TOC reconstruction
3. Phase 3 — region-aware table reconstruction
4. Phase 4 — logical family resolver upgrade
5. Phase 5 — semantic and chunking alignment
6. Phase 6 — persistence and debug visibility
7. Phase 7 — downstream propagation

Reason:

- the highest leverage is fixing structure before downstream semantics
- semantic arbitration now needs to happen immediately after structure because the `sdt_1` export showed real category drift even where tables were otherwise readable
- debug visibility should still land early enough to verify each stage
- downstream prompt and answer quality should be the consequence of better parsing, not the substitute for it

---

## Final Recommendation

Yes, page identity is part of the answer, but it is not enough.

The enterprise-standard fix is to introduce:

- page orientation awareness
- page-local visual regions
- region-local reading order
- region-aware TOC and table reconstruction
- archetype-first table understanding above raw marker lists

That gives you a reusable foundation for:

- TOC
- manuals
- datasheets
- certificates
- reports
- future technical documents with side-by-side structures

This is the correct next architecture step if the goal is a top-tier document-grounded RAG system whose parsing understands the document more like a human reader.
