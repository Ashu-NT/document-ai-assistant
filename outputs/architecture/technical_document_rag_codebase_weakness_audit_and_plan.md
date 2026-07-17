# Technical Document RAG Codebase Weakness Audit And Upgrade Plan

## Scope

This audit focuses on the technical-document path that matters most for enterprise RAG quality:

- manuals
- certificates
- drawings
- reports
- datasheets

It specifically evaluates whether the current codebase is strong enough to answer the most common real user questions:

- maintenance tasks, intervals, and procedures
- spare-parts lists, often split by component
- troubleshooting tables and remedy steps
- manufacturer and supplier information
- technical specifications and operating limits
- certificate validity / reference / scope
- drawing title-box and component references

This document now serves as both an audit and a living upgrade-status plan. It records current weaknesses, implemented progress, and the next recommended phases.

## Executive Summary

The codebase has a much better foundation than a basic RAG system. It already has:

- a staged parsing workflow
- a real document graph
- section-aware chunking
- table-family metadata
- extraction schemas
- structured evidence retrieval
- structured answer-context assembly

That said, the system is not yet at the level where it can be called fully enterprise-grade for technical-document QA across varied unseen document layouts.

The biggest current issue is architectural imbalance:

- document understanding still depends too heavily on heuristic text repair and format-specific row normalization
- several core workflows are too large and own too many responsibilities directly
- some “structured” evidence survives only until the prompt boundary, where it is still serialized back into text/JSON-in-a-string
- retrieval and answer quality still compensate for parsing/chunking/table-structure gaps that should be solved earlier

The result is a system that can perform very well on some documents, but can still regress badly on new manuals, multi-column layouts, continuation tables, scanned certificates, and complex mixed-structure pages.

The correct next direction is not “more answer tricks.” It is:

1. strengthen parsing and layout understanding
2. formalize table reconstruction and table semantics
3. reduce orchestration bloat and silent fallbacks
4. preserve typed evidence deeper into retrieval and answer generation

## Implementation Status Update (2026-07-17)

This audit is now partially historical. Several items that were originally listed as open have since been implemented or partially implemented.

Implemented since the earlier audit draft:

- OCR runtime policy wiring now exists:
  - `src/application/workflows/parsing/ocr/parsing_ocr_policy.py`
  - `src/application/orchestrator/ingestion/parsing_runtime_builder.py`
  - `src/application/workflows/parsing/parsing_workflow.py`
- canonical OCR enrichment now uses one explicit OCR-service contract instead of dynamic method probing:
  - `src/application/workflows/parsing/canonical_element_ocr_enricher.py`
- ingestion now fails earlier when a non-empty finalized graph produces zero chunks:
  - `src/application/workflows/ingestion/ingestion_workflow.py`
- settings fallback handling was reduced and centralized further:
  - `src/application/workflows/common/settings_resolver.py`
  - `src/application/services/answer_generation/answer_generation_service.py`
  - `src/application/workflows/parsing/builders/document_graph_builder.py`
- low-level table-row parsing primitives were moved out of the domain package:
  - `src/application/workflows/parsing/tables/rows/*`
  - the temporary compatibility facades were removed and direct imports were updated
- the generic key-value row projection helper was also moved into the parsing normalization layer:
  - `src/application/workflows/parsing/tables/normalization/key_value_row_projection.py`

Already present in the codebase before this update, but underrepresented in the original audit:

- page layout analysis and lane-aware reading-order repair:
  - `src/application/workflows/parsing/layout/page_layout_analyzer.py`
  - `src/application/workflows/parsing/normalizers/docling_document_normalizer.py`
- TOC-aware table reconstruction and hierarchy support:
  - `src/application/workflows/parsing/normalizers/docling_toc_table_row_reconstructor.py`
  - `src/application/workflows/parsing/normalizers/table_layout/docling_parallel_toc_reconstructor.py`
  - `src/application/workflows/parsing/builders/section_hierarchy/toc/*`
- logical table-family continuation already uses layout-aware signals:
  - `src/application/workflows/parsing/tables/logical_table_family_resolver.py`

Current active next phase:

- finish relocating the remaining higher-level table normalizers/renderers out of `src/domain/assets/table_rows/`
- reduce domain-level helper behavior in `src/domain/assets/table_asset.py`
- continue Phase 1 and Phase 2 as hardening/expansion of existing layout and table-reconstruction foundations, not as greenfield additions

## What Is Already Strong

The following parts of the codebase are moving in the right direction and should be preserved:

- `src/application/workflows/parsing/parsing_workflow.py`
  - explicit staged parsing with timing/progress
- `src/application/workflows/parsing/builders/section_builder.py`
  - real hierarchy resolution and section-path relinking
- `src/application/workflows/parsing/builders/document_graph_builder.py`
  - graph-first architecture instead of direct chunk-only parsing
- `src/application/workflows/parsing/builders/document_graph/graph_chunk_builder.py`
  - chunk metadata already carries logical table family, category, header paths, axis summary, and table-row window data
- `src/application/workflows/extraction/response/schemas/*`
  - extraction payloads are already typed instead of free-form dicts
- `src/application/workflows/retrieval/structured/structured_evidence_resolver.py`
  - structured evidence is already part of retrieval, not just answer decoration
- `src/application/workflows/question_answering/answer_context/*`
  - answer context is no longer only raw chunks
- `src/application/prompts/answer_generation/prompt_context/*`
  - there is already an explicit projection layer between retrieved evidence and prompt generation

That is a good base. The remaining weaknesses are about boundaries, ownership, and fidelity.

## Core Weaknesses

### 1. Ingestion orchestration is too concentrated

Primary evidence:

- `src/application/workflows/ingestion/ingestion_workflow.py:87`
- `src/application/workflows/ingestion/ingestion_workflow.py:169`

`IngestionWorkflow` is still an oversized end-to-end orchestrator at 800+ LOC. Its `run()` path owns:

- hash creation
- duplicate detection
- ingestion-run lifecycle
- parsing
- registration
- classification
- post-classification finalization
- extraction
- semantic linking
- embedding/indexing
- status/event updates

Why this is risky:

- any stage change has a large blast radius
- retry / partial-failure logic is harder to reason about
- test isolation is weaker than it should be
- production and debug/evaluation behaviors are more likely to drift

Fix direction:

- split stage ownership into dedicated stage coordinators
- keep `IngestionWorkflow` as a thin orchestration shell
- move duplicate handling, run-state persistence, extraction/indexing coordination, and failure mapping into smaller collaborators

### 2. Extraction is decomposed, but still centers on a large workflow and a legacy-style combined prompt

Primary evidence:

- `src/application/workflows/extraction/extraction_workflow.py:66`
- `src/application/workflows/extraction/extraction_workflow.py:194`
- `src/application/prompts/extraction/combined/combined_extraction_prompt_builder.py:6`
- `src/application/prompts/extraction/compatibility/legacy_extraction_prompt_builder.py:8`
- `src/application/workflows/extraction/candidates/extraction_prompt_narrowing_service.py:17`

The extraction package has improved a lot. It now contains:

- batching
- retry coordination
- payload schemas
- builders
- response repair
- merging

But the active workflow still builds extraction prompts through `CombinedExtractionPromptBuilder`, which directly inherits the legacy combined schema prompt.

Why this is risky:

- the active extraction path is still dominated by a very large combined JSON contract
- prompt complexity remains high for small models
- prompt narrowing happens after the existence of the combined prompt, not instead of it
- future extraction families remain tightly coupled

Fix direction:

- keep the current schema-based safety
- replace the active “combined legacy-shaped prompt” as the primary extraction mode
- move to family-planned extraction batches driven by deterministic candidate selection
- keep compatibility prompt builders only as compatibility builders, not as the live default path

### 3. Parsing has good stage structure, but OCR control is fragmented

Primary evidence:

- `src/application/workflows/parsing/parsing_workflow.py:42`
- `src/application/workflows/parsing/canonical_element_ocr_enricher.py:11`
- `src/config/settings/docling_settings.py:6`
- `src/config/settings/ocr_settings.py:6`

OCR behavior is currently spread across three separate paths:

- Docling OCR
- canonical element OCR enrichment
- page OCR fallback

The settings are also split between:

- `DOCLING_ENABLE_OCR`
- `ENABLE_PROVIDER_OCR`
- `OCR_PAGE_FALLBACK_ENABLED`
- `OCR_REGION_FALLBACK_ENABLED`

Why this is risky:

- users can disable one OCR path and still trigger another
- operational behavior is harder to predict
- debugging OCR cost/performance issues is harder than it should be
- the runtime policy is defined across settings rather than through a single OCR strategy object

Status update:

- partially implemented
- a real OCR runtime policy now exists, but the remaining work is to simplify the settings surface area and remove overlapping flag semantics

Fix direction:

- keep one OCR runtime policy resolver for parsing as the single execution authority
- simplify configuration around explicit OCR modes such as:
  - docling-only
  - provider-asset-only
  - provider-page-fallback
  - provider-region-fallback
  - no-ocr
- keep `ParsingWorkflow` consuming one resolved OCR policy rather than many scattered booleans

### 4. Core parsing/table heuristics are still too heuristic-heavy and partly misplaced in the domain layer

Primary evidence:

- `src/application/workflows/parsing/tables/rows/table_row_canonicalizer.py`
- `src/domain/assets/table_rows/spare_parts_table_normalizer.py`
- `src/application/workflows/parsing/tables/families/logical_table_family_row_merger.py:14`

The current system does real table cleanup, but much of it is still based on:

- label heuristics
- umbrella-header heuristics
- transposed key-value heuristics
- specialized normalizers per table family

The low-level helper layer has now started moving out of `src/domain/assets/table_rows/`, but the relocation is not complete yet. Higher-level normalizers and renderers still live there, which keeps the architectural boundary only partially corrected.

Why this is risky:

- domain models become coupled to parser quirks
- new document/table families are harder to support cleanly
- table normalization logic becomes harder to reuse across parsing, extraction, retrieval, and answering

Status update:

- partially implemented
- low-level primitives are now in `src/application/workflows/parsing/tables/rows/`
- remaining higher-level normalizers/renderers still need relocation

Fix direction:

- finish moving row-canonicalization and table-structure repair logic fully into parsing/application infrastructure layers
- reserve domain assets for stable document concepts, not parser cleanup heuristics
- introduce a formal table-reconstruction pipeline:
  - page-region segmentation
  - column-band inference
  - continuation detection
  - header-span reconstruction
  - row-wrap / multiline-cell repair
  - table typing and semantic projection

### 5. Chunking is metadata-rich, but still downstream of imperfect layout understanding

Primary evidence:

- `src/application/workflows/parsing/builders/document_graph/graph_chunk_builder.py:15`
- `src/application/workflows/parsing/builders/chunking/*`
- `src/application/workflows/parsing/builders/section_builder.py:20`

The chunking layer already carries good metadata:

- `logical_table_family_id`
- `table_category`
- `header_paths`
- `axis_summary`
- chunk part numbering

That is strong.

The weakness is upstream:

- if page layout is misread
- if a multi-column page is flattened badly
- if a wrapped row is not reconstructed
- if a continued table is split incorrectly

then chunking only preserves already-degraded structure.

Why this is risky:

- retrieval can rank the “right” chunk but still deliver structurally broken evidence
- answer generation receives semantically incomplete tables
- table-heavy manuals degrade disproportionately

Fix direction:

- treat chunking as a consumer of layout-aware table and section structure
- do not keep teaching chunking to fix problems that should have been fixed at page/layout/table-reconstruction stage

### 6. Structured answer context exists, but the generic LLM path still consumes serialized text

Primary evidence:

- `src/application/workflows/question_answering/answer_context/answer_context_organizer.py:37`
- `src/application/prompts/answer_generation/answer_prompt_builder.py:24`
- `src/application/prompts/answer_generation/prompt_context/projectors/prompt_context_projector.py:26`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py:10`
- `src/config/settings/prompt_context_settings.py:6`

The system now builds:

- `StructuredAnswerContext`
- projected prompt-context bundles
- serialized structured evidence payloads

This is a major improvement over raw chunk dumping.

But the generic LLM still ultimately receives:

- instruction text
- schema text
- serialized JSON payload text
- raw-source appendix text

Why this is risky:

- structure is preserved in Python, then partially flattened at the prompt boundary
- prompt caps can silently reduce coverage
- `PROMPT_CONTEXT_INCLUDE_SOURCE_TABLE_ROWS=false` means rich row data may exist in memory but not reach the generic model path
- multiple representations of the same fact can create prompt noise

Fix direction:

- keep deterministic renderers for stable answer classes
- for the generic LLM path, move toward a true typed prompt context contract
- reduce duplication between:
  - source prose
  - key-values
  - structured entities
  - tables
  - relationships
- make raw appendix explicitly secondary, not co-equal with structured payload

### 7. Retrieval quality logic is powerful but too monolithic and heuristic-dense

Primary evidence:

- `src/application/workflows/retrieval/retrieval_workflow.py:49`
- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py:118`
- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py:428`

The retrieval stack already has:

- query analysis
- structured evidence injection
- hybrid retrieval
- deduplication
- context expansion

The weak point is the heuristic concentration in `SqlKeywordScorer`.

Why this is risky:

- scoring behavior is hard to reason about
- tuning one retrieval problem can regress another
- many concerns live in one scorer:
  - identifier matching
  - phrase matching
  - section-path relevance
  - chunk-type fit
  - structured-fit bonuses
  - TOC/revision/noise penalties

Fix direction:

- split ranking into explicit feature calculators
- emit feature vectors / scoring diagnostics per candidate
- keep the final scorer compositional
- let structured evidence ranking and table-specific ranking become first-class rather than additive heuristics

### 8. Duplicate utility logic still exists in active layers

Primary evidence:

- `src/application/workflows/shared/structured_evidence_deduplication.py:13`
- `src/application/workflows/shared/structured_evidence_deduplication.py:42`
- `src/application/langgraph/nodes/node_utils.py:99`
- `src/application/langgraph/nodes/node_utils.py:165`

There is still live duplication of:

- identifier deduplication
- structured-entity deduplication

The two versions are not exactly the same; they intentionally differ in strictness.

Why this is risky:

- behavior drift is easy
- fixing one dedupe bug may not fix the other path
- “same name, slightly different semantics” is hard to maintain

Fix direction:

- keep one canonical implementation
- expose strict/lenient policy explicitly through a typed strategy or options object
- stop re-defining the same helper names in different layers

### 9. Dynamic interface checks and broad fallback patterns hide failures

Primary evidence:

- `src/application/workflows/parsing/canonical_element_ocr_enricher.py:58`
- `src/application/workflows/parsing/builders/document_graph_builder.py` top-level settings fallback helpers
- `src/application/services/answer_generation/answer_generation_service.py:122`
- `src/application/workflows/retrieval/retrieval_context_expander.py`
- `src/application/workflows/common/settings_resolver.py`

Examples of risky patterns:

- dynamic `getattr()` contract switching for OCR service methods
- `except Exception` settings fallbacks in core runtime code
- silent defaulting when configuration imports fail

Why this is risky:

- real configuration or contract errors can be masked
- runtime behavior can degrade silently instead of failing loudly
- debugging becomes slower

Fix direction:

- keep broad exception guards in scripts if needed
- reduce them in core application/runtime paths
- prefer explicit adapter contracts and explicit settings-resolution failures
- when fallback is required, emit structured diagnostics, not only warnings

### 10. File responsibility drift is still present in several important modules

Large files currently include:

- `src/application/workflows/ingestion/ingestion_workflow.py`
- `src/application/workflows/extraction/extraction_workflow.py`
- `src/application/services/answer_generation/answer_generation_service.py`
- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py`
- `src/application/langgraph/reflection/validation/reflection_validator.py`
- `src/application/agent_runtime/presenters/console/graph_result_renderer.py`
- `src/application/workflows/parsing/builders/document_graph_builder.py`

Why this is risky:

- responsibilities drift back into god-objects
- test setup becomes heavier
- review quality drops because too much logic changes in one file

Fix direction:

- keep the repo rule: one file, one responsibility
- split remaining large files into grouped subpackages instead of flat growth

### 11. Reflection and presentation logic are improving, but still policy-heavy and brittle

Primary evidence:

- `src/application/langgraph/reflection/validation/reflection_validator.py:23`
- `src/application/agent_runtime/presenters/console/graph_result_renderer.py:23`

Both modules clearly improved, but they still contain a lot of policy in one place:

- maintenance special cases
- spare-parts special cases
- identifier inventory overrides
- rendering notes / citations / sections / footers together

Why this is risky:

- every new answer class adds more branching
- regressions become easy in interactive agent output
- validation policy and presentation policy are not as compositional as they should be

Fix direction:

- split rule packs by answer family
- keep the top-level validator/renderer as dispatch/orchestration only

## Technical-Document Specific Gaps

These are the gaps most directly blocking “96% accurate, well-structured technical-document understanding.”

### Manuals

Weak points:

- maintenance matrices still rely on heuristic row repair
- troubleshooting row continuation is not guaranteed
- spare-parts tables can still degrade when headers/rows wrap badly
- chunk retrieval may surface evidence, but answer formatting can still underuse exact table structure

### Certificates

Weak points:

- scanned-document OCR policy is still fragmented
- validity/approval/reference extraction depends too much on extraction prompt success instead of guaranteed structural cues
- contact/manufacturer/certificate metadata relationships are present but not yet a first-class certificate reasoning model

### Drawings

Weak points:

- title blocks and reference boxes depend heavily on parser/table/layout fidelity
- multi-zone page layouts need stronger region-aware handling

### Datasheets

Weak points:

- performance/specification matrices still depend on table normalization heuristics
- ordering / technical data / operating limits should be governed by a reusable table typing layer, not document-specific repair

### Reports

Weak points:

- mixed prose + table + checklist pages are still vulnerable to layout flattening
- electrical / inspection / additional-info blocks need stronger typed evidence projection

## Bad Coding / Architecture Findings To Fix

These are specific code-quality findings that should be addressed even if retrieval quality were already acceptable.

### A. Parsing heuristics in the domain layer

Files:

- `src/domain/assets/table_rows/spare_parts_table_normalizer.py`
- `src/domain/assets/table_rows/structured_row_renderer.py`
- `src/domain/assets/table_asset.py`

Fix:

- continue moving parser/table repair heuristics out of domain and into parsing/application-level table reconstruction packages
- leave only stable asset concepts in the domain layer

### B. Duplicate dedupe helpers

Files:

- `src/application/workflows/shared/structured_evidence_deduplication.py`
- `src/application/langgraph/nodes/node_utils.py`

Fix:

- one canonical helper plus strictness policy

### C. Dynamic OCR contract fallback

File:

- `src/application/workflows/parsing/canonical_element_ocr_enricher.py`

Fix:

- stop checking for method names dynamically
- require one explicit OCR-service result contract

Status:

- implemented for the canonical OCR enricher path

### D. Silent settings fallback in runtime code

Files include:

- `src/application/services/answer_generation/answer_generation_service.py`
- `src/application/workflows/parsing/builders/document_graph_builder.py`
- `src/application/workflows/common/settings_resolver.py`

Fix:

- centralize settings resolution
- fail fast on invalid settings for production workflows
- keep fallback logic only where truly necessary

Status:

- partially implemented

### E. Active dependency on a legacy-shaped extraction prompt

Files:

- `src/application/prompts/extraction/combined/combined_extraction_prompt_builder.py`
- `src/application/prompts/extraction/compatibility/legacy_extraction_prompt_builder.py`

Fix:

- fully separate compatibility prompt builders from the active extraction path

## Recommended Implementation Plan

## Phase 0: Correctness And Boundary Cleanup

Status:

- partially implemented

Goals:

- reduce silent failure risk
- stabilize runtime behavior
- remove obvious duplication

Actions:

- split `IngestionWorkflow` stage ownership into small coordinators
- unify identifier/entity dedupe helpers
- replace dynamic OCR service probing with one explicit OCR result contract
- centralize OCR runtime policy resolution
- continue moving parsing/table heuristics out of `src/domain/assets/table_rows/`
- fail fast when a non-empty parsed document produces zero final chunks
- reduce `except Exception` usage in core runtime code paths

## Phase 1: Layout-Aware Document Understanding

Status:

- foundation already exists
- the active work is hardening and expansion, not adding it from zero

Goals:

- make parsing stronger for unseen technical-document layouts

Actions:

- harden existing page-layout zone modeling before table/section interpretation
- expand multi-column and left/right region awareness already present in normalization/layout analysis
- formalize table continuation detection across pages more consistently
- formalize row-wrap and multiline-cell reconstruction more deeply
- preserve numbered section hierarchy consistently, including TOC-derived hints where reliable

## Phase 2: Enterprise Table Reconstruction

Status:

- in progress
- low-level row primitives were moved to the parsing layer in this implementation slice

Goals:

- make table understanding a first-class subsystem

Actions:

- create a reusable table reconstruction contract
- separate:
  - physical table extraction
  - logical family merge
  - header/span reconstruction
  - semantic table typing
  - typed row projection
- keep table categorization generic:
  - maintenance
  - troubleshooting
  - spare parts
  - technical specification
  - performance curve
  - certificate / approval / validity
  - generic structured table

Important:

- no document-specific header hacks
- normalization must rely on generic structural and semantic cues, not current DB documents

## Phase 3: Chunking As A Consumer Of Better Structure

Goals:

- stop asking chunking to repair layout failures

Actions:

- keep current metadata-rich chunk model
- make chunk assembly consume reconstructed logical tables and richer section topology
- ensure chunk types are driven by direct evidence first, inherited path second
- keep numbering and section lineage as part of retrieval-friendly context

## Phase 4: Extraction Modernization

Goals:

- reduce prompt overload and improve reliability on small/local models

Actions:

- replace active combined legacy-style prompt path with family-planned extraction batches
- let candidate selection choose extraction families first
- keep pydantic/typed payload validation strict
- preserve batch isolation and partial progress
- persist extraction diagnostics at family/batch level for review

## Phase 5: Retrieval Simplification And Stronger Structured Ranking

Goals:

- make ranking easier to maintain and easier to debug

Actions:

- decompose `SqlKeywordScorer` into feature calculators
- treat structured evidence ranking as a first-class retrieval branch
- create table-intent ranking features that use:
  - table category
  - logical table family
  - header paths
  - axis summary
  - row window
- keep hybrid retrieval, but make features auditable

## Phase 6: Typed Answer Context At The Prompt Boundary

Goals:

- stop degrading typed evidence into prompt noise

Actions:

- keep `StructuredAnswerContext`
- keep deterministic renderers
- redesign generic LLM prompt context so structured evidence remains the primary payload
- keep raw appendix explicitly secondary
- remove unnecessary duplication across:
  - sources
  - key-values
  - tables
  - structured entities
  - relationship text

## Phase 7: Answering / Reflection / Presentation Cleanup

Goals:

- improve output quality without adding brittle special cases

Actions:

- split reflection rules by answer family
- split console rendering into small presentation blocks
- preserve enterprise-quality grounded output
- ensure table answers prefer typed table evidence over generic prose summarization whenever structure is available

## Non-Negotiable Design Rules For Future Work

- do not tune logic to current database documents only
- do not hardcode specific current-document values into structural detection
- do not keep parsing heuristics inside domain packages
- do not let retrieval/answering compensate forever for parsing/layout errors
- do not grow remaining hotspot files past the single-responsibility threshold
- do not reintroduce parallel legacy and active implementations for the same capability

## Priority Order

Recommended order:

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5
7. Phase 6
8. Phase 7

That order matters.

If parsing/layout/table structure is not strengthened first, later retrieval and answering improvements will continue to be brittle and document-sensitive.

## Final Verdict

The system is no longer a weak prototype. It has many of the right enterprise building blocks.

But it is not yet “top-notch enterprise technical-document RAG” across unseen manuals, certificates, drawings, reports, and datasheets.

The main reason is not lack of features.

The main reason is that too much downstream intelligence is still compensating for upstream document-understanding instability.

The path to excellence is clear:

- make layout understanding stronger
- make table reconstruction first-class
- keep chunking downstream of better structure
- modernize extraction away from the active legacy-shaped combined prompt
- preserve typed evidence deeper into answer generation

That is the upgrade path most likely to produce stable, scalable, document-agnostic quality.
