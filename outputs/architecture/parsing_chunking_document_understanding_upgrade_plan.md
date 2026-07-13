# Parsing and Chunking Document Understanding Upgrade Plan

## Executive Summary

The current pipeline already has a strong structural backbone:

- `src/application/workflows/parsing/parsing_workflow.py` runs `DoclingParser -> DoclingDocumentNormalizer -> DocumentGraphBuilder`
- `src/application/workflows/parsing/builders/section_builder.py` and `section_hierarchy/*` already infer section hierarchy using heading levels, numbering, layout heuristics, and TOC cues
- `src/application/workflows/parsing/builders/chunking/*` already supports document-type-aware chunk policies, structured fragment builders, semantic chunk typing, and section-aware merging
- persisted `TableAsset` data is rehydrated later and reused by retrieval, extraction, and answer grounding

That said, the system still does not understand technical documents as well as a human would in four critical areas:

1. logical tables versus physical table fragments
2. numbered section paths as first-class structure
3. TOC as a reusable document-outline prior
4. table semantics and table categories across parsing, retrieval, and answer grounding

The main gap is not that parsing is missing. The main gap is that the parsed structure is not being normalized into strong, reusable document-understanding artifacts before chunking and retrieval consume it.

This plan upgrades the current design without replacing the existing architecture.

## Scope

This plan covers:

- parsing normalization
- section hierarchy and section-path quality
- TOC exploitation
- logical table modeling
- table categorization
- chunking of structured technical evidence
- retrieval hydration of tables and related chunks
- answer-context exposure of structured tables

This plan does not cover:

- answer-generation prompt redesign
- LLM provider changes
- repository redesign outside the existing graph/document persistence model

## Current Active Flow

### 1. Parsing and normalization

- `src/application/workflows/parsing/parsing_workflow.py`
  - calls `DoclingParser.parse()`
  - calls `DoclingDocumentNormalizer.normalize()`
  - optionally runs canonical OCR enrichment and page OCR fallback
  - calls `DocumentGraphBuilder.build()`

- `src/application/workflows/parsing/normalizers/docling_document_normalizer.py`
  - materializes canonical elements
  - stores section path, table markdown, table rows, dimensions, captions, OCR text in element metadata

- `src/application/workflows/parsing/normalizers/docling_table_extractor.py`
  - extracts physical table rows from Docling table cells
  - exports markdown
  - computes row/column counts

### 2. Section hierarchy

- `src/application/workflows/parsing/builders/section_builder.py`
  - collects section headers
  - resolves hierarchy
  - builds `DocumentSection`
  - assigns elements to active sections

- `src/application/workflows/parsing/builders/section_hierarchy/section_hierarchy_resolver.py`
  - combines:
    - `HeadingLevelStrategy`
    - `TocPageRangeStrategy`
    - `NumberingHierarchyStrategy`
    - `LayoutHeuristicStrategy`

- `src/application/workflows/parsing/builders/section_hierarchy/toc_page_range_strategy.py`
  - already scans early pages for TOC anchors
  - parses TOC entries
  - matches TOC entries to actual headers

- `src/application/workflows/parsing/builders/section_hierarchy/section_path_relinker.py`
  - sanitizes section paths
  - rebuilds parent-child relationships from sanitized paths

### 3. Chunk generation

- `src/application/workflows/parsing/builders/document_graph/graph_chunk_builder.py`
  - delegates to `SectionChunkBuilder`

- `src/application/workflows/parsing/builders/chunking/builders/section_chunk/section_chunk_builder.py`
  - creates runtime from document/chunking profile
  - builds section fragments
  - packs fragments into payloads
  - builds overview chunks
  - deduplicates payloads

- `src/application/workflows/parsing/builders/chunking/builders/fragment/chunk_fragment_builder.py`
  - builds per-element fragments
  - handles generic text, tables, pictures
  - runs structured fragment extraction first

- `src/application/workflows/parsing/builders/chunking/builders/structured_section_fragment_builder.py`
  - orchestrates structured evidence window extraction

- `src/application/workflows/parsing/builders/chunking/builders/chunk_payload_factory.py`
  - resolves payload section path
  - assembles chunk content
  - resolves final `ChunkType`
  - builds embedding text

### 4. Table reuse after parsing

- `src/infrastructure/db/repositories/document/document_graph_reader.py`
  - rehydrates `TableAsset` from persisted element metadata

- `src/application/workflows/extraction/batching/extraction_table_chunk_hydrator.py`
  - replaces partial table chunk text with full table text for extraction

- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
  - replaces retrieved chunk content with full saved table text for QA

- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
  - builds answer-facing tables from hydrated `table_rows`

## What Is Already Good

### 1. The repo already has the right high-level boundaries

- parsing
- normalization
- section hierarchy
- chunking runtime and policies
- retrieval hydration
- answer-context projection

This means we do not need a rewrite. We need stronger document-understanding artifacts inside the existing seams.

### 2. TOC and numbering are already partially wired

The codebase is not starting from zero:

- TOC rows are already parsed
- TOC entries are already matched to headers
- numbering and layout strategies already interact
- section paths are already sanitized and relinked

This is a good base for a stronger outline-aware system.

### 3. Structured chunking already exists

`StructuredFamilySpecFactory` and the structured family builders already prove that the system can emit domain-relevant chunks instead of only flat text windows.

That is the correct direction.

## Current Weaknesses

### 1. Logical tables are not modeled strongly enough

Current table handling is still mostly physical-table-driven:

- `DoclingTableExtractor` yields rows from a single physical table item
- `TableAsset` stores one table asset at a time
- retrieval and extraction hydrators work per `table_id`

This breaks down for:

- multi-page tables
- split TOC tables
- maintenance matrices continued on the next page
- long spare-parts tables
- datasheet tables with continuation headers

### 2. Section paths are useful, but still mid-level

`sanitize_section_path()` helps reduce noise, but current paths are still not strong enough for enterprise retrieval because:

- numbering is not preserved as a first-class reusable structure
- display path and normalized path are conflated
- sibling-reset and numbering-reset heuristics are local cleanup, not an explicit outline model

### 3. TOC is only used as a hierarchy hint

`TocPageRangeStrategy` helps assign section levels, but the TOC is not promoted into a reusable document-outline artifact that downstream chunking and retrieval can consult.

That means the system misses:

- where major sections start and stop
- which pages belong to which headings
- continuation expectations for long sections and tables
- better section-path naming based on official TOC wording

### 4. Table semantic typing is still too narrow

`TableFragmentBuilder.table_chunk_type()` only directly identifies spare-parts tables, then falls back to `GENERAL`.

Later semantic classification helps through:

- `ChunkSemanticSignalExtractor`
- `ChunkTableSignalScorer`
- `ChunkTypeResolver`

But table meaning is still mostly inferred after the fact instead of being recognized as a first-class parsing/chunking concern.

### 4.1 Current compatibility helpers still embed narrow assumptions

Some of the current table convenience logic is useful, but it should not become the enterprise semantic contract.

Concrete example from the live code:

- `src/domain/assets/table_asset.py`
  - `_looks_schedule_marker_header()` still assumes a narrow code set like `D/W/M/Q/S/A`

That is acceptable as a compatibility heuristic for rendering helper text, but it is too narrow to drive core table understanding for unseen technical documents.

The upgraded design should explicitly treat helpers like this as:

- compatibility-only
- low-confidence conveniences
- never the primary semantic classifier

### 5. Hydration and answer projection still flatten too much

The system preserves useful raw data, but later stages still reduce it:

- `TableEvidenceHydrator` hydrates per `table_id`, not logical table family
- only one `table_rows_json` payload is preserved per hydrated chunk
- `AnswerTableProjector` treats each source independently
- `AnswerTableSchemaInferer` has only a small set of table kinds

This weakens:

- multi-page table completeness
- structured answer quality
- retrieval relevance for table-heavy questions

## Design Principles For The Upgrade

### 1. Treat numbered outline as a first-class document signal

The system should preserve:

- numbered heading text
- normalized heading text
- TOC-derived start page
- resolved section ancestry

### 2. Separate physical table assets from logical table families

One physical Docling table is not always one business table.

The system should distinguish:

- physical table asset
- logical table family
- logical table category
- family member order
- family continuation boundaries

### 3. Use generic technical-document heuristics, not corpus-specific markers

Table understanding must rely on:

- header roles
- repeated headers across pages
- caption similarity
- section semantics
- page adjacency
- row shape
- identifier/unit patterns

Not on document-specific names from the current database.

### 4. Keep current architecture, but strengthen artifacts

The right move is:

- enrich canonical/table/section artifacts
- feed them into chunking
- propagate them into retrieval and answer grounding

The wrong move is:

- scattering ad-hoc fixes across answer prompts
- hardcoding current document labels
- bypassing parsing with QA-only hacks

### 5. Treat upstream parser accuracy as helpful but insufficient

The current Docling runtime already exposes strong upstream parsing controls through:

- `src/infrastructure/parsing/docling/docling_converter_factory.py`

Those settings can improve physical extraction quality, but this plan must not assume that better upstream table detection alone solves:

- logical multi-page table families
- merged-cell semantics
- category inference
- retrieval-ready table understanding

In other words:

- better parser precision helps
- richer document-understanding artifacts are still required

### 6. Keep pandas as an optional debug/export layer, not the domain model

DataFrame-style views can be helpful for:

- debugging
- developer export
- inspection tooling

But pandas should not become the canonical table representation inside the application/domain path.

The canonical source of truth should remain application-owned structured artifacts that preserve:

- span-aware cells
- logical family membership
- category/confidence
- compatibility row grids

Optional pandas views can be derived later for tooling only

## Target Upgrade Plan

## Required Cross-Cutting Contracts Before Implementation

These contracts must be defined before implementation starts. Without them, the upgrade will improve parsing ideas on paper but still lose structure before retrieval and QA can use it.

## Canonical table artifact contract

### Goal

Define one canonical table representation that survives the full pipeline.

### Current gap

Today the durable table shape is effectively:

- `markdown`
- `rows`
- `row_count`
- `column_count`

That is not enough for:

- merged-cell semantics
- multi-line cell handling
- logical table families
- table categories with confidence

### Required contract

The canonical table artifact should include:

1. physical identity
   - `table_id`
   - source element reference
   - page range

2. span-aware cells
   - `row_start`
   - `row_end`
   - `col_start`
   - `col_end`
   - `row_span`
   - `col_span`
   - `raw_text`
   - `normalized_text`
   - optional `raw_lines`

3. derived views
   - logical grid
   - flattened rows
   - markdown

4. table understanding metadata
   - `logical_table_family_id`
   - `family_index`
   - `family_total`
   - `continuation_role`
   - `table_category`
   - `table_category_confidence`
   - optional `secondary_categories`
   - `header_signature`
   - optional `header_bands`

### Important rule

`rows: list[list[str]]` remains a compatibility view. It must not remain the only source of truth.

## Persistence and rehydration contract

### Goal

Guarantee that richer table structure survives DB round-trip.

### Current gap

Current rehydration restores only:

- `markdown`
- `table_rows`
- `row_count`
- `column_count`

from persisted parser metadata.

### Required contract

The plan must define:

1. where richer table metadata is serialized
2. how it is deserialized
3. what must remain reconstructible after reload without re-running Docling

### Minimum persistence guarantee

After persistence and reload, the system must still recover:

- span-aware cells
- logical family membership
- table category
- compatibility row grids

## Chunk and retrieval propagation contract

### Goal

Ensure table understanding reaches retrieval and answer grounding.

### Current gap

Chunks currently preserve `table_ids`, but not:

- logical table family id
- table category
- category confidence
- row-family position

### Required contract

Table-aware chunks should propagate through:

- `src/application/workflows/parsing/builders/chunking/builders/chunk_payload_factory.py`
- `src/application/workflows/parsing/builders/document_graph/graph_chunk_builder.py`
- `src/infrastructure/db/mappers/document/chunk_mapper.py`
- `src/infrastructure/db/mappers/retrieval/retrieved_chunk_mapper.py`

The minimum metadata contract is:

- `logical_table_family_id`
- `table_category`
- `table_category_confidence`
- physical `table_ids`
- optional row-range within family

This metadata must survive through persisted chunks and retrieval mappers.

## Fallback tiers for incomplete structure

### Goal

Avoid brittle behavior when Docling structure is partial.

### Current gap

The current extractor can already fall back to markdown/text export, so the plan cannot assume span-aware cells always exist.

### Required fallback tiers

1. Tier A: span-aware structure available
   - full merged-cell and row-reconstruction logic

2. Tier B: row grid only available
   - row-based semantic inference
   - no merged-cell guarantees

3. Tier C: markdown/text only available
   - conservative parsing only
   - no high-confidence structural claims

### Important rule

The system should degrade gracefully, not fail hard because one table lacks span metadata.

## Migration and compatibility contract

### Goal

Keep current row-based consumers working while richer structure is introduced.

### Current gap

Current downstream consumers still assume row grids, especially:

- table evidence hydration
- answer table projection
- extraction table hydration

### Required contract

The plan should explicitly state:

1. existing `rows` stays available as derived compatibility output
2. existing `table_rows_json` stays supported during migration
3. richer span-aware and family metadata is additive first
4. row-only consumers are upgraded incrementally

## Ambiguity and confidence handling

### Goal

Avoid overconfident categorization on ambiguous tables.

### Required contract

Every categorized logical table should support:

- `table_category`
- `table_category_confidence`
- optional `secondary_categories`
- optional `supporting_signals`

### Behavior

- high confidence:
  - usable for retrieval preference and chunk typing
- medium confidence:
  - usable as a soft ranking hint
- low confidence:
  - preserve as `general_table` or weak category only

## Performance and storage guardrails

### Goal

Keep the richer representation practical for large manuals and reports.

### Required guardrails

The plan should include:

1. profiling on large documents
2. parser metadata size monitoring
3. limits on duplicated derived forms
4. no unnecessary duplication of:
   - raw text
   - normalized text
   - markdown
   - row grids
   - span-aware cells

### Important rule

Store one canonical source plus necessary derived views, not many redundant copies.

## Phase 1. Section Path and Outline Foundation

### Goal

Make section paths robust enough to serve retrieval, chunking, and answer grounding.

### Current files to extend

- `src/application/workflows/parsing/builders/section_builder.py`
- `src/application/workflows/parsing/builders/section_hierarchy/section_hierarchy_resolver.py`
- `src/application/workflows/parsing/builders/section_hierarchy/section_path_relinker.py`
- `src/application/workflows/parsing/builders/chunking/text/section_path_sanitizer.py`
- `src/application/workflows/parsing/builders/section_hierarchy/toc_page_range_strategy.py`

### Changes

1. Preserve numbered section labels explicitly.
   - keep human-readable numbered labels in `section_path`
   - add normalized comparison helpers instead of stripping numbering too early

2. Split path responsibilities conceptually.
   - display path for humans
   - normalized path for matching/scoring
   - outline number/path tokens for hierarchy reasoning

3. Promote TOC matches into stronger section metadata.
   - matched TOC title
   - matched TOC numbering
   - TOC start page hint

4. Ensure path sanitation never destroys valid numbering structure.
   - use numbering-aware resets only when hierarchy genuinely conflicts
   - prefer keeping official numbering over aggressive cleanup

### Expected benefit

- better retrieval path matching
- better chunk section labels
- better human-readable references
- less path drift between parse and answer layers

## Phase 2. TOC as a Reusable Outline Artifact

### Goal

Use the TOC as a durable structure prior, not just a one-time section-level heuristic.

### Current files to extend

- `src/application/workflows/parsing/builders/section_hierarchy/toc/toc_entry_parser.py`
- `src/application/workflows/parsing/builders/section_hierarchy/toc_page_range_strategy.py`
- `src/application/workflows/parsing/builders/document_graph_builder.py`

### Changes

1. Introduce a reusable outline artifact inside the parsing workflow layer.
   - TOC entries
   - numbering
   - normalized title
   - page anchors
   - matched header ids

2. Support TOC continuation across multiple physical tables/pages.
   - continuation detection by repeated row/header structure
   - page adjacency
   - same TOC heading context

3. Expose outline data to chunking runtime inputs.
   - section confidence
   - official short titles
   - page priors for major sections

### Expected benefit

- better major-section segmentation
- better page-aware retrieval hints
- stronger section-path quality for long manuals and reports

## Phase 3. Logical Table Family Resolution

### Goal

Resolve multi-fragment table evidence into logical tables before chunking and retrieval consume it.

### Current files to extend

- `src/application/workflows/parsing/normalizers/docling_table_extractor.py`
- `src/application/workflows/parsing/normalizers/docling_document_normalizer.py`
- `src/application/workflows/parsing/builders/document_graph_builder.py`
- `src/infrastructure/db/repositories/document/document_graph_reader.py`
- `src/domain/assets/table_asset.py`
- `src/infrastructure/db/mappers/document/element_mapper.py`

### New grouped area recommended

- `src/application/workflows/parsing/tables/`
  - `logical_table_family.py`
  - `logical_table_family_resolver.py`
  - `table_continuation_detector.py`
  - `table_header_normalizer.py`
  - `table_family_merge_policy.py`

### Changes

1. Keep physical `TableAsset`, but add logical family resolution above it.

2. Detect continuation by generic signals:
   - same or near-identical normalized headers
   - page adjacency
   - same section assignment
   - same caption or caption family
   - same row shape / column count
   - split tail/head row continuation patterns

3. Assign family metadata:
   - `logical_table_family_id`
   - `family_index`
   - `family_total`
   - `continuation_role`
   - `normalized_header_signature`
   - `table_category`
   - `table_category_confidence`

4. Rehydrate logical table families from persisted graph data.

5. Preserve compatibility row grids as derived views rather than canonical structure.

### Expected benefit

- TOC tables become single logical outlines
- maintenance schedules become complete evidence objects
- spare-part and datasheet tables stop fragmenting semantically

## Phase 4. Generic Table Semantic Classification

### Goal

Recognize the type of technical table generically and early.

### Current files to extend

- `src/application/workflows/parsing/builders/chunking/builders/fragment/table_fragment_builder.py`
- `src/application/workflows/parsing/builders/chunking/builders/semantic_signals/chunk_table_signal_scorer.py`
- `src/application/workflows/parsing/builders/chunking/builders/semantic_signals/chunk_semantic_signal_extractor.py`
- `src/application/workflows/question_answering/answer_context/tables/table_header_semantics.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_schema_inferer.py`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`

### Target generic table families

- maintenance schedule / maintenance interval matrix
- troubleshooting matrix
- technical data / datasheet specification table
- spare parts / BOM table
- certification / particulars table
- identifier register
- connection / terminal table
- sensor / instrument list
- operating limits / pressure-temperature table
- general record table

### Target table categories for retrieval

These should become explicit, reusable categories rather than only being implied by chunk text:

- `maintenance_table`
- `maintenance_interval_table`
- `troubleshooting_table`
- `technical_data_table`
- `datasheet_specification_table`
- `spare_parts_table`
- `certification_table`
- `identifier_table`
- `connection_table`
- `sensor_instrument_table`
- `operating_limits_table`
- `toc_table`
- `general_table`

### Changes

1. Move table semantics into dedicated, reusable detectors.

2. Score table meaning from:
   - header roles
   - schedule interval headers
   - identifier-bearing columns
   - units and value patterns
   - row density and row shape
   - section title/path context

3. Make direct table evidence outrank inherited section path when they conflict.
   - this is especially important for safety-heavy ancestors containing technical tables

4. Store the resolved table category as first-class metadata.
   - on the logical table family
   - on emitted table-driven chunks
   - in retrieval-facing payload metadata where appropriate

5. Do not rely on narrow document-specific schedule aliases.
   - `D/W/M/Q/A`
   - `x/check/1`
   - exact current-manual labels
   should be treated only as examples of broader semantics, not as the design itself

6. Introduce explicit confidence handling.
   - `table_category_confidence`
   - optional secondary categories
   - weak categories remain soft ranking hints, not hard filters

7. Respect fallback tiers.
   - span-aware tables
   - row-grid-only tables
   - markdown/text-only tables

### Expected benefit

- fewer wrongly typed table chunks
- better table-aware retrieval routing and filtering
- better retrieval chunk filtering
- better answer-context formatting

## Phase 5. Logical-Table-Aware Chunk Generation

### Goal

Chunk technical tables as meaningful evidence units, not accidental physical fragments.

### Current files to extend

- `src/application/workflows/parsing/builders/chunking/builders/fragment/chunk_fragment_builder.py`
- `src/application/workflows/parsing/builders/chunking/builders/fragment/table_fragment_builder.py`
- `src/application/workflows/parsing/builders/chunking/builders/chunk_payload_factory.py`
- `src/application/workflows/parsing/builders/chunking/policies/section_merge_policy.py`
- `src/application/workflows/parsing/builders/document_graph/graph_chunk_builder.py`

### Changes

1. Build fragments from logical table families when available.

2. Support two chunk modes for tables:
   - atomic full-family chunk for compact and medium tables
   - row-group chunking for very large tables while preserving family identity

3. Preserve family metadata on chunks:
   - table family id
   - physical table ids
   - logical table category
   - logical table category confidence
   - row span within family
   - continuation markers

4. Keep overview/context chunks as companions, not primary evidence.

5. Make merge policy numbering-aware and family-aware.
   - do not merge unrelated numbered siblings
   - do not merge across logical table boundaries unless explicitly intended

6. Propagate retrieval-useful table metadata through persisted chunks.
   - no runtime-only table categorization that disappears after reload

### Expected benefit

- much stronger retrieval for structured evidence
- cleaner answer grounding
- less need to repair chunk semantics later

## Phase 6. Retrieval Hydration and Table Expansion

### Goal

When any member of a logical table family is retrieved, the system should be able to hydrate the right complete evidence.

### Current files to extend

- `src/application/workflows/extraction/batching/extraction_table_chunk_hydrator.py`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/retrieval/context_expansion/document_chunk_index.py`
- `src/infrastructure/db/mappers/document/chunk_mapper.py`
- `src/infrastructure/db/mappers/retrieval/retrieved_chunk_mapper.py`

### Changes

1. Hydrate by logical table family, not only by `table_id`.

2. Keep multiple family members when needed instead of dropping everything after the first seen `table_id`.

3. Let context expansion load:
   - same table family
   - same numbered subsection
   - companion prose only after table evidence is assembled

4. Make table category available to retrieval policy and ranking.
   - maintenance queries can prefer maintenance tables
   - troubleshooting queries can prefer troubleshooting tables
   - identifier/specification queries can prefer identifier/specification tables
   - TOC tables can be aggressively down-ranked after outline extraction

5. Preserve fallback behavior for low-structure tables.
   - if only row grid exists, hydrate row grid
   - if only markdown exists, hydrate conservatively without pretending strong structure

### Expected benefit

- complete tables in QA and extraction
- fewer misleading partial-table answers
- better reuse of persisted parsing work

## Phase 7. Answer-Context Table Projection

### Goal

Expose structured tables to answer generation in a way that preserves their semantics.

### Current files to extend

- `src/application/workflows/question_answering/answer_context/tables/answer_table.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_schema_inferer.py`
- `src/domain/assets/table_asset.py`

### Changes

1. Extend `AnswerTable` beyond single-source physical tables.
   - logical family identity
   - continuation order
   - normalized headers
   - table semantics
   - optional grouped header bands
   - optional row-label inheritance metadata

2. Replace generic row echo with schema-aware row serialization.
   - key-value tables
   - schedule matrices
   - record tables
   - identifier tables

3. Keep the raw markdown, but expose structured rows as a first-class artifact.

### Expected benefit

- better enterprise answer quality
- stronger structured grounding
- less flattening before the LLM sees evidence

## Table Categorization and Retrieval

### Why this matters

Table categorization should be treated as a retrieval signal, not only as a rendering detail.

A user asking for:

- maintenance intervals
- troubleshooting causes/remedies
- technical data
- spare parts
- serial numbers / part numbers

is often asking for a table-shaped answer even when they do not say "table".

If the system knows that a chunk belongs to a categorized logical table family, retrieval can:

- rank the right evidence higher
- suppress noisy prose when the real answer is tabular
- expand complete table families instead of only one split chunk
- feed answer generation with more faithful structured evidence

### Retrieval use of table categories

The retrieval stack should eventually consume table categories through existing retrieval metadata paths rather than a parallel architecture.

Priority examples:

- maintenance intent
  - prefer `maintenance_table` and `maintenance_interval_table`
- troubleshooting intent
  - prefer `troubleshooting_table`
- specification intent
  - prefer `technical_data_table`, `datasheet_specification_table`, `operating_limits_table`
- identifier intent
  - prefer `identifier_table`, `spare_parts_table`, `sensor_instrument_table`
- document navigation intent
  - use `toc_table` for structure only, not as answer evidence unless explicitly asked

### Important rule

`toc_table` is useful for document understanding, but normally should not compete with answer evidence during retrieval once outline extraction has already happened.

## Generic Table Recognition Strategy

### Core principle

Table recognition must be semantic and structural, not tied to the exact labels seen in the current database.

The system should not depend on only:

- `D`, `W`, `M`, `Q`, `A`
- `x`, `check`, `1`
- one exact header spelling
- one exact manual format

Those patterns are useful signals, but they are not the primary design.

### What the system should infer instead

For each logical table, the system should infer:

1. table purpose
   - maintenance
   - troubleshooting
   - technical data
   - spare parts
   - identifiers
   - connection
   - certification
   - TOC

2. column roles
   - task/action
   - interval/frequency
   - component/equipment
   - identifier/code
   - label
   - value
   - unit
   - notes
   - cause
   - symptom
   - remedy

3. cell behavior
   - descriptive text cells
   - numeric/specification cells
   - boolean/applicability cells
   - interval-expression cells
   - identifier-bearing cells

4. structural form
   - key-value table
   - record table
   - matrix table
   - multi-row grouped record table
   - continuation table

### Merged-cell identification

Merged cells should be identified from Docling cell span metadata, not guessed only from flattened row text.

The current code already has the right low-level signal in:

- `src/application/workflows/parsing/normalizers/docling_table_extractor.py`

That extractor reads table-cell coordinates such as:

- `start_row_offset_idx`
- `end_row_offset_idx`
- `start_col_offset_idx`
- `end_col_offset_idx`

This is the correct foundation because a merged cell is fundamentally a span, not a text pattern.

#### Current weakness

The current `_extract_rows()` path flattens cells into:

- `list[list[str]]`

That is useful for many downstream steps, but it loses key structure:

- whether a header spans multiple columns
- whether a left-side label spans multiple rows
- whether blank cells are intentional children of a merged parent
- whether a table has grouped header bands

#### Required upgrade

The parsing layer should preserve a span-aware canonical table cell model before building flattened rows.

Recommended shape:

- `row_start`
- `row_end`
- `col_start`
- `col_end`
- `row_span`
- `col_span`
- `text`
- optional role hints later

A cell is merged when:

- `row_span > 1`
- or `col_span > 1`

#### Why this matters

Merged cells often carry high-value semantics in technical documents:

- multi-column group headers in datasheets
- grouped schedule bands in maintenance matrices
- parent labels for several child rows
- category or subsystem labels in spare-part and instrument tables
- section blocks in certificates and reports

If span information is lost too early, downstream logic cannot reliably tell whether:

- a blank child cell should inherit a parent label
- several columns belong under one grouped header
- a table is a matrix versus a flat record table

#### How merged cells should be used

Merged-cell semantics should feed:

1. header hierarchy detection
   - top header band
   - child header band
   - grouped column families

2. row-label inheritance
   - a left-side merged label can apply to multiple following rows

3. matrix recognition
   - grouped interval columns
   - grouped status columns
   - grouped specification subcolumns

4. logical table family merging
   - repeated merged header structure is a strong continuation signal

5. answer and retrieval projections
   - preserve grouped meaning instead of exposing only flattened text

#### Recommended implementation shape

This should live in a small grouped table-structure area, not inside one large extractor file.

Recommended grouped area:

- `src/application/workflows/parsing/tables/structure/`
  - `table_cell_span.py`
  - `span_aware_table_grid.py`
  - `merged_cell_detector.py`
  - `header_band_resolver.py`
  - `row_label_inheritance_resolver.py`

#### Important rule

The flattened row grid should remain a derived view for convenience.

It should not be the only table representation.

The canonical source of truth should become:

- span-aware cells
- derived logical grid
- derived flattened rows

This allows later table categorization and retrieval logic to behave intelligently even when documents use merged headers, grouped schedule columns, or multi-row category labels.

### Multi-line cell content and row reconstruction

Another important issue is that one cell in a row may contain:

- one line of text

while another cell in the same row contains:

- two or more wrapped lines of text

This must not cause the system to treat the row as multiple rows.

#### Core rule

Line breaks inside a cell are cell-internal formatting, not row boundaries.

The system should reconstruct rows from table-cell coordinates and spans, not from:

- newline count
- visual wrapping
- markdown rendering alone

#### Current risk

If downstream logic relies too heavily on flattened markdown or naive row parsing, it can misread:

- wrapped descriptions
- long denomination fields
- long troubleshooting remedies
- specification values with units and notes
- certificate particulars with long text

as if the table had extra rows or broken row alignment.

#### Required upgrade

The span-aware table model should preserve each extracted cell as one logical cell even when its text contains multiple visual lines.

That means:

1. row identity comes from row indices, not rendered line count
2. cell text should be normalized within the cell
3. wrapped lines should be joined carefully into one logical value unless there is evidence they are true sub-records
4. derived row grids should be built from coordinate placement, not markdown splitting

#### Cell text normalization

For each cell, the system should maintain:

- raw text
- normalized single-value text
- optional line-preserved text for debugging

Recommended normalization behavior:

- collapse cosmetic line wraps into spaces
- preserve meaningful separators when present
- keep units, symbols, and identifier punctuation intact
- avoid splitting a single logical value into multiple pseudo-cells

Examples:

- a long description wrapped over two lines remains one cell value
- `2000 hours / 2 years` remains one interval expression
- a remedy sentence wrapped over several lines remains one remedy cell

#### When multi-line content may be meaningful

Not every multi-line cell should be collapsed blindly.

Some cells may intentionally contain:

- bulleted sub-items
- stacked identifier aliases
- multiple approval codes
- multiple operating conditions

So the normalization layer should preserve both:

- canonical single-value text for matching/classification
- raw line-aware text for advanced semantic parsing when needed

#### Recommended implementation shape

This belongs alongside merged-cell and span-aware table structure handling.

Recommended grouped area:

- `src/application/workflows/parsing/tables/structure/`
  - `table_cell_text_normalizer.py`
  - `row_reconstruction_policy.py`
  - `table_row_builder.py`
  - `cell_line_wrap_resolver.py`

#### Why this matters for retrieval

If row reconstruction is wrong, retrieval quality drops because:

- identifiers may separate from their descriptions
- spare part numbers may separate from denomination columns
- maintenance task text may separate from interval markers
- troubleshooting causes may separate from remedies
- specification rows may become noisy or incomplete

So this is not only a formatting problem. It is a core evidence-integrity problem.

### Better way to detect maintenance matrices

Instead of hardcoding only `D/W/M/Q/A`, the system should detect maintenance-style matrices from a combination of generic signals:

1. one or more left-side descriptive columns
   - task
   - activity
   - inspection item
   - maintenance operation
   - component/action text

2. repeated right-side low-entropy columns
   - cells mostly contain short markers, ticks, bullets, yes/no-like values, or blanks
   - these columns behave like applicability/frequency flags rather than prose/value fields

3. interval-like header semantics
   - calendar frequencies:
     - daily, day, days
     - weekly, week, weeks
     - monthly, month, months
     - quarterly
     - annually, annual, yearly
   - runtime intervals:
     - 100 h
     - 250 hours
     - every 2000 h
     - 2000 hours / 2 years
   - event intervals:
     - before startup
     - after shutdown
     - after cleaning
     - before operation

4. matrix shape
   - many columns
   - narrow cells
   - strong repetition pattern
   - often a long first column and many short schedule columns

This means a table can still be recognized as a maintenance matrix even when the headers are:

- `Daily | Weekly | Monthly`
- `Day | Week | Year`
- `100h | 500h | 2000h / 2 years`
- `Before start-up | After cleaning | Annual inspection`

### Better way to detect applicability markers

The system should not only look for `x`.

It should classify marker-like cells by behavior:

- very short token
- repeated across many rows
- high sparsity
- low lexical variety
- often aligned under interval/event columns

Examples include:

- `x`
- `X`
- `1`
- `yes`
- `ok`
- checkmarks
- filled circles / squares
- bullets
- small repeated glyphs

The important point is not the exact token. The important point is that the column behaves like a boolean applicability column.

### Better way to detect interval expressions

The system should introduce a generic interval-expression parser for table headers and cells.

That parser should normalize expressions such as:

- `daily`
- `every day`
- `weekly`
- `every 2 weeks`
- `monthly`
- `100 hours`
- `100 h`
- `2000h / 2 years`
- `annually`
- `before start-up`

into canonical interval semantics:

- calendar interval
- runtime-hours interval
- event-based interval
- mixed interval

This should be implemented as reusable parsing logic, not mixed into one-off header aliases.

### Proposed implementation shape

This should live in a grouped parsing or answer-context subpackage rather than one large file.

Recommended grouped area:

- `src/application/workflows/parsing/tables/semantics/`
  - `table_semantic_classifier.py`
  - `table_role_inferer.py`
  - `table_matrix_detector.py`
  - `interval_expression_parser.py`
  - `boolean_marker_detector.py`
  - `table_shape_analyzer.py`

### Why this is better

This approach generalizes to unseen technical documents because it reasons from:

- structure
- repetition
- role semantics
- interval syntax
- cell behavior

instead of relying on one corpus's exact vocabulary.

## Phase 8. Debug and Inspection Tooling

### Goal

Make document-understanding artifacts inspectable during development and evaluation.

### Current files to extend

- `scripts/debug_parse_document.py`
- `scripts/export_document_table_assets.py`

### Changes

1. Show logical table families.
   - family id
   - member physical tables
   - continuation order
   - family semantic type

2. Show numbered section-path variants.
   - raw path
   - sanitized display path
   - normalized matching path

3. Show TOC outline and matched headers.

### Expected benefit

- faster diagnosis
- safer future tuning
- less guesswork when retrieval misses happen

## Test Plan

## Parsing and section hierarchy

- TOC split across multiple physical tables is resolved into one outline
- numbered section paths are preserved
- sanitization removes branding/noise without destroying numbering
- matched TOC numbering is attached to the correct section/header

## Logical table family resolution

- same-header next-page tables merge into one logical family
- unrelated same-page small tables do not merge
- continued maintenance tables preserve member order
- split TOC tables preserve logical family identity
- logical family metadata survives DB persist/rehydrate

## Table semantics

- maintenance schedule tables classify correctly from generic headers
- troubleshooting matrices classify correctly from generic cause/remedy headers
- technical/specification tables outrank inherited safety context
- spare-parts tables still classify correctly
- resolved logical tables receive stable table categories
- weak or ambiguous categories remain soft hints rather than overcommitted labels

## Chunking

- logical family metadata propagates onto final chunks
- large logical tables can be row-group chunked without losing family identity
- section merge respects numbering and semantic boundaries
- chunk table metadata survives DB persist/rehydrate

## Retrieval and QA

- retrieving any table-family member can hydrate the full logical table evidence
- table-category-aware retrieval prefers the right table families for matching intents
- answer table projection preserves headers and row semantics
- continuation tables do not disappear after first-family hydration

## Table structure edge cases

- merged header spanning multiple columns is preserved
- merged left label spanning multiple rows supports row-label inheritance
- one multi-line wrapped cell beside single-line neighbor cells remains one row
- row-grid-only fallback tables remain usable
- markdown/text-only fallback tables do not claim high-confidence structure

## Acceptance Criteria

The upgrade is successful when all of the following are true:

1. section numbering remains visible and reusable end to end
2. TOC is represented as a reusable outline artifact, not only a one-time hint
3. multi-page technical tables resolve into logical table families
4. table chunk typing is driven primarily by direct table evidence
5. resolved logical tables receive explicit reusable categories
6. retrieval can hydrate complete logical tables instead of only physical fragments
7. answer-context tables preserve structured semantics instead of flattening everything into generic text
8. debug tooling makes all of the above inspectable

## Recommended Implementation Order

1. Phase 1: section path and outline foundation
2. Phase 2: TOC outline artifact
3. Phase 3: logical table family resolution
4. Phase 4: generic table semantic classification
5. Phase 5: logical-table-aware chunk generation
6. Phase 6: retrieval hydration and table expansion
7. Phase 7: answer-context table projection
8. Phase 8: debug tooling

## Final Recommendation

The next upgrade should not start in answer generation.

The highest-value work is deeper in parsing and chunking:

- preserve numbered structure better
- elevate TOC into a durable outline model
- model logical tables explicitly
- let retrieval and QA consume that stronger structure

That is the cleanest path to making the system understand technical documents more like a human and less like a flat text retriever.
