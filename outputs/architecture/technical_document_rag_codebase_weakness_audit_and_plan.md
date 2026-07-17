# Technical Document RAG Codebase Weakness Audit And Upgrade Plan

## Audit Context

Date:

- 2026-07-17

Scope:

- full technical-document pipeline
- ingestion
- parsing
- OCR
- table reconstruction
- chunking
- extraction
- embedding
- retrieval
- answer generation
- guardrails
- agent runtime and presentation

Current runtime context:

- documents were recently reingested into SQLite and Qdrant
- extraction was intentionally skipped for the latest ingest pass because of cost/time
- this means the live runtime currently reflects a parse/chunk/embed heavy mode more than a full semantic-extraction mode

Important constraint:

- this plan is intentionally document-agnostic
- no recommendation below should depend on FWC12, Pressure transmitter, PURO 30, or any other currently ingested sample
- the target system must generalize across thousands of unseen manuals, certificates, drawings, reports, and datasheets

## Executive Summary

The codebase now has a strong architectural base:

- a real staged ingestion pipeline
- a graph-first parsing model
- layout-aware and table-aware parsing foundations
- hybrid retrieval
- structured answer-context assembly
- typed LLM response schemas for several major capabilities
- run-state tracking through `IngestionRun`

However, it is still not at a stable enterprise-grade level for large-scale heterogeneous technical-document QA.

The main issue is no longer "missing features". The main issue is uneven maturity across layers:

- upstream parsing and table understanding are improving quickly
- downstream retrieval and answering still compensate for upstream ambiguity too often
- structured evidence exists, but it is not consumed consistently across all answer paths
- core orchestration is still concentrated in a few large files
- runtime modes such as parse-only, parse+embed, and full semantic extraction are not yet explicit enough as first-class operating profiles

The most important next step is not to add more document-specific heuristics. It is to tighten boundaries and make the system more generic:

1. make parsing and table structure contracts stronger and clearer
2. make retrieval intent and evidence-family selection stricter
3. make identifier and table answers consume structured table evidence directly
4. separate semantic-enrichment modes from structural ingestion modes
5. split orchestration hotspots into smaller stage-owned coordinators

## What Is Already Strong

The following parts are solid and should be preserved:

- `src/application/workflows/ingestion/`
  - explicit ingestion stages, `IngestionRun`, stage events, retry paths
- `src/application/workflows/parsing/parsing_workflow.py`
  - staged parsing with progress and timings
- `src/application/workflows/parsing/builders/`
  - graph-first document build instead of chunk-first parsing
- `src/application/workflows/parsing/tables/`
  - a large amount of table normalization, family composition, row repair, and semantic projection already exists
- `src/application/workflows/retrieval/retrieval_workflow.py`
  - real workflow boundary with query analysis, hybrid retrieval, deduplication, context expansion, and guardrail adapters
- `src/application/workflows/retrieval/structured/`
  - structured evidence retrieval exists as a first-class path
- `src/application/workflows/question_answering/answer_context/`
  - answer generation is no longer driven only by raw chunks
- `src/application/services/answer_generation/`
  - deterministic renderers exist for high-value answer families
- `src/application/workflows/extraction/response/schemas/`
  - extraction responses are now strongly typed instead of free-form dicts

These are meaningful enterprise foundations. The remaining work is mostly about consistency, ownership, and genericity.

## End-To-End Weaknesses

### 1. Orchestration is still too concentrated in a few hotspot files

Largest current hotspots in `src/`:

- `src/application/workflows/ingestion/ingestion_workflow.py` - 895 LOC
- `src/application/evaluation/retrieval/benchmarking/corpus/resolution/retrieval_benchmark_corpus_document_resolver.py` - 505 LOC
- `src/application/workflows/extraction/extraction_workflow.py` - 418 LOC
- `src/application/workflows/question_answering/answer_pipeline/answer_generation_pipeline.py` - 344 LOC
- `src/application/workflows/parsing/builders/document_graph_builder.py` - 343 LOC
- `src/application/services/answer_generation/answer_generation_service.py` - 230 LOC after Phase 0 refactor
- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py` - 178 LOC after Phase 0 refactor

Why this matters:

- changes in one stage create large blast radii
- testing becomes integration-heavy even for local behavior changes
- fallback logic and business rules accumulate in the same file
- enterprise maintainability drops as soon as rules become more numerous

Root issue:

- the architecture direction is correct
- the code ownership boundaries are still not thin enough inside the orchestration layer

### 2. Parsing owns too many adjacent concerns at runtime boundaries

Relevant files:

- `src/application/workflows/parsing/parsing_workflow.py`
- `src/infrastructure/parsing/docling/docling_parser.py`
- `src/application/workflows/parsing/ocr/parsing_ocr_policy.py`

Current strengths:

- parsing stages are explicit
- OCR policy is centralized better than before

Remaining weaknesses:

- `ParsingWorkflow` still coordinates parsing, normalization, OCR enrichment, page fallback OCR, validation, and report writing directly
- `DoclingParser` still contains broad fallback behavior around settings loading
- parsing report writers are still wired into the production workflow path rather than being cleanly isolated as optional observers

Why this matters:

- production parsing and debug/reporting are closer than they should be
- settings resolution can still degrade quietly in some lower-level parser defaults
- adding a new OCR or parser strategy increases coupling across the same workflow

### 3. OCR is improved, but the runtime model is still more complicated than it should be

Relevant files:

- `src/application/workflows/parsing/ocr/parsing_ocr_policy.py`
- `src/application/workflows/parsing/canonical_element_ocr_enricher.py`
- `src/application/workflows/parsing/ocr/`
- `src/infrastructure/ai/ocr/`

Current shape:

- Docling OCR can be enabled/disabled
- provider OCR can enrich canonical elements
- page fallback OCR exists
- region fallback OCR exists

Weakness:

- this is still one conceptual "OCR capability" represented by several runtime paths
- the system still needs one explicit document OCR strategy model that answers:
  - structural OCR only?
  - asset OCR only?
  - sparse page fallback?
  - full page fallback?
  - region fallback?

Why this matters:

- future scaling needs predictable cost/performance behavior
- operations need one place to reason about OCR mode selection
- enterprise ingestion should expose one explicit OCR decision, not just a collection of flags

### 4. Table understanding is strong at parsing time but not consumed consistently downstream

Relevant files:

- `src/application/workflows/parsing/tables/`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py`

Current strengths:

- logical table families exist
- table category, shape, header paths, axis summary, and row projections exist
- hydrated table evidence reaches QA

Observed weakness:

- the same structured table evidence is not used equally by all answer classes
- some answer paths still rely on key-value extraction or generic chunk prose even when typed table rows are available
- the system has excellent table metadata, but downstream consumers do not yet exploit it uniformly

Why this matters:

- enterprise RAG quality in technical docs depends on tables more than on prose
- if structured tables are available but ignored by some answer routes, answer quality will still look inconsistent and document-sensitive

### 5. Retrieval intent and chunk-type preference rules are still too permissive

Relevant files:

- `src/application/workflows/retrieval/retrieval_query_analyzer.py`
- `src/application/workflows/retrieval/retrieval_query_intent_inferer.py`
- `src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py`
- `src/infrastructure/retrieval/rerankers/deterministic/intent_chunk_type_scorer.py`
- `src/infrastructure/retrieval/rerankers/deterministic/table_query_evidence_scorer.py`
- `src/application/workflows/question_answering/evidence/table_focused_evidence_pruner.py`

Current strengths:

- deterministic intent analysis exists
- chunk-type preferences exist
- reranking exists
- table-focused pruning exists

Current weakness:

- focused intents still admit too many weakly-related chunk families
- table-focused pruning only removes low-value scaffolding companions
- it does not fully suppress mismatched direct-evidence table families

Consequence:

- identifier, maintenance, specification, and table questions can still carry noisy evidence into answer generation
- the system answers better than before, but still wastes context budget on evidence that should have been rejected earlier

### 6. Identifier answers do not yet fully consume structured table evidence

Relevant files:

- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py`
- `src/application/workflows/question_answering/answer_context/key_value_extractor.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
- `src/application/workflows/question_answering/answer_pipeline/structured_fact_joiner.py`

Current strength:

- identifier answers can use:
  - persisted identifiers
  - key-values
  - joined structured facts

Current weakness:

- the identifier renderer still does not consume `AnswerTable` directly
- if part numbers or serial numbers live primarily inside hydrated table rows and were not persisted as identifiers during extraction, the renderer can still miss them

Why this matters:

- manuals and datasheets often expose identifiers in tables, not prose
- this is a generic technical-document pattern, not a current corpus quirk

### 7. Structured evidence is still joined late and partly compensatory

Relevant files:

- `src/application/workflows/retrieval/structured/structured_evidence_resolver.py`
- `src/application/workflows/question_answering/answer_pipeline/structured_evidence_merger.py`
- `src/application/workflows/question_answering/answer_pipeline/structured_fact_joiner.py`

Current strength:

- structured evidence exists and can be merged into retrieval/QA

Weakness:

- the structured branch is still partly additive and late
- when extraction is skipped, the structural retrieval path still works, but semantic retrieval becomes thin
- the answer pipeline compensates by stitching semantic evidence back into chunk context later

Why this matters:

- the system needs two explicit and equally valid runtime modes:
  - structural mode
  - structural + semantic mode
- right now those modes exist operationally, but not cleanly enough as first-class architecture concepts

### 8. Extraction is modernized, but the default active prompt path is still too combined

Relevant files:

- `src/application/workflows/extraction/extraction_workflow.py`
- `src/application/workflows/extraction/batching/extraction_batch_executor.py`
- `src/application/prompts/extraction/CombinedExtractionPromptBuilder`
- `src/application/prompts/extraction/narrowed/`

Current strengths:

- batch execution exists
- partial progress exists
- per-batch retry exists
- typed response schemas exist
- candidate narrowing exists

Weakness:

- the default extraction workflow still starts from a combined prompt-builder path
- narrowing refines the prompt, but the capability is still conceptually centered on one large multi-family contract

Why this matters:

- small local models remain fragile under large mixed extraction prompts
- future extraction families will be harder to evolve independently
- semantic extraction should be more planner-like at the family level, not just prompt-reduced after the fact

### 9. The prompt boundary still flattens too much evidence into one serialized payload

Relevant files:

- `src/application/prompts/answer_generation/prompt_context/projectors/`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py`
- `src/application/services/answer_generation/answer_generation_service.py`

Current strengths:

- structured context exists in Python
- typed answer tables and maintenance entries exist
- prompt bundles are explicit

Weakness:

- source content, key-values, tables, structured entities, and relationship views still end up coexisting in one serialized JSON-in-text prompt
- the system preserves structure better than before, but it still does not enforce a truly typed LLM-facing contract end to end

Why this matters:

- the generic LLM still receives too much duplicated evidence
- prompt noise increases as parsing quality and structured evidence richness improve

### 10. Retrieval ranking is powerful but still concentrated in one scorer

Relevant files:

- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py`
- `src/infrastructure/retrieval/rerankers/deterministic/`

Current strength:

- the ranking stack already includes many enterprise-relevant signals

Weakness:

- `sql_keyword_scorer.py` still owns too much feature logic in one place
- feature calculation, weighting, and penalty logic are not yet decomposed cleanly enough

Why this matters:

- tuning becomes harder over time
- regression diagnosis remains slower than necessary
- feature observability is weaker than it should be for enterprise retrieval tuning

### 11. Runtime modes and configuration are still too distributed

Relevant files:

- `src/config/settings/*.py`
- `src/application/orchestrator/`
- `src/application/workflows/common/settings_resolver.py`

Current strength:

- settings are typed and modularized

Weakness:

- there are still too many loosely-related flags across ingestion, OCR, extraction, prompt context, and retrieval
- the system lacks a small set of explicit runtime profiles such as:
  - parse_only
  - parse_and_embed
  - full_semantic_ingest
  - benchmark_debug
  - interactive_demo

Why this matters:

- enterprise operations need predictable deployment modes
- performance and quality tradeoffs should be selectable intentionally, not inferred from a large flag surface

### 12. Local-Qdrant operation is not a robust multi-process development mode

Relevant files:

- `src/infrastructure/retrieval/vector/qdrant_vector_store.py`
- runtime builders under `src/application/orchestrator/`

Current weakness:

- local Qdrant storage is effectively single-process in practice for debug/audit tooling
- sequential use is fine
- parallel debug probes and multiple local runtimes are operationally fragile

Why this matters:

- this limits large-scale evaluation and developer tooling ergonomics
- the codebase needs a cleaner distinction between:
  - local single-process dev mode
  - shared Qdrant server mode

### 13. Maintainability debt remains in presentation and evaluation layers too

Hotspots outside the core pipeline:

- `src/application/agent_runtime/presenters/console/graph_result_renderer.py` - 359 LOC
- `src/application/langgraph/reflection/validation/reflection_validator.py` - 381 LOC
- `src/application/langgraph/nodes/question_answering/retry_retrieval_node.py` - 355 LOC
- `src/application/evaluation/retrieval/benchmarking/corpus/resolution/retrieval_benchmark_corpus_document_resolver.py` - 505 LOC

Why this matters:

- even if the retrieval core improves, policy and presentation drift can reintroduce brittle behavior
- enterprise polish depends on small, explicit formatting and validation units

## Non-Document-Specific Design Rules

All future upgrades should obey these rules:

- do not hardcode current corpus values, labels, or identifiers
- do not add logic that only works for one manual family
- use structure before text heuristics whenever possible
- treat tables, OCR, section paths, identifiers, and structured entities as generic evidence families
- keep one file, one responsibility
- keep active files below the repo threshold whenever possible
- remove facades and compatibility shims once direct imports are safe
- avoid parallel implementations of the same capability
- make degraded modes explicit instead of silently falling back

## Target End State

The target system should have four clear operating layers:

1. Structural ingestion
- parse
- normalize
- reconstruct layout and tables
- build graph
- chunk
- embed

2. Semantic enrichment
- classify
- extract semantic entities
- link semantic relationships
- optionally generate questions

3. Retrieval
- structural retrieval
- semantic retrieval
- hybrid ranking
- context expansion

4. Answering
- typed answer context
- deterministic answer paths for stable classes
- generic LLM path with typed evidence contract
- reflection and presentation as downstream policy layers

This should work in both modes:

- structural-only mode
- structural-plus-semantic mode

## Phased Upgrade Plan

### Phase 0 - Stabilize Boundaries And Reduce Silent Degradation

Goals:

- reduce silent runtime drift
- make modes explicit
- shrink the largest blast-radius files

Status:

- in progress
- implemented slice:
  - explicit ingestion runtime profile resolution
  - explicit structural-only versus semantic-enriched diagnostics
  - workflow-level enforcement so semantic linking cannot run implicitly when extraction is disabled
  - CLI/JSON ingestion output now surfaces runtime profile information
  - `IngestionWorkflow` now delegates parsing work to a dedicated parsing stage runner
  - `IngestionWorkflow` now delegates registration work to a dedicated registration stage runner
  - `IngestionWorkflow` now delegates classification work to a dedicated classification stage runner
  - `IngestionWorkflow` now delegates finalization work to a dedicated finalization stage runner
  - `IngestionWorkflow` now delegates extraction/identifier/linking work to a dedicated extraction stage runner
  - `IngestionWorkflow` now delegates embedding/indexing work to a dedicated vector indexing stage runner
  - `AnswerGenerationService` now delegates settings resolution, prompt execution/retry, result assembly, and compound-question limitation handling to dedicated collaborators
  - `SqlKeywordScorer` now delegates morphology helpers, scoring config, penalties, and score-component assembly to grouped scoring modules

Actions:

- split `IngestionWorkflow` into stage-owned coordinators
- split `AnswerGenerationService` into:
  - request resolution
  - deterministic dispatch
  - prompt execution
  - schema repair/retry
  - result assembly
- split `SqlKeywordScorer` into feature calculators plus a final combiner
- remove remaining broad fallback behavior from low-level parser defaults and core runtime code
- introduce explicit ingestion/runtime profiles

Implemented in this slice:

- `src/application/workflows/ingestion/runtime/`
  - `IngestionRuntimeProfile`
  - `IngestionRuntimeCapabilities`
  - `IngestionRuntimeProfileResolver`
- `src/application/workflows/ingestion/stages/`
  - `ParsingStageRunner`
  - `ParsingStageResult`
  - `RegistrationStageRunner`
  - `ClassificationStageRunner`
  - `ClassificationStageResult`
  - `FinalizationStageRunner`
  - `FinalizationStageResult`
  - `ExtractionStageRunner`
  - `ExtractionStageResult`
  - `VectorIndexStageRunner`
  - `VectorIndexStageResult`
- `src/application/orchestrator/ingestion/ingestion_orchestrator.py`
  - resolves runtime capabilities from settings once at composition time
- `src/application/workflows/ingestion/ingestion_workflow.py`
  - consumes resolved capabilities and blocks implicit semantic-linking drift
  - delegates parsing, registration, classification, finalization, extraction, and vector-indexing clusters to stage-owned collaborators
- `src/application/workflows/ingestion/pipeline/extraction_retry_step.py`
  - uses the same resolved runtime capabilities during extraction retry
- `src/application/services/answer_generation/`
  - `answer_generation_service.py`
    - reduced to orchestration-only ownership around request resolution, deterministic dispatch, and prompt execution handoff
  - `answer_generation_service_settings.py`
    - owns answer-generation settings defaults and fallback logging
  - `execution/answer_generation_prompt_executor.py`
    - owns schema-aware LLM execution and one corrective retry
  - `execution/answer_generation_result_assembler.py`
    - owns `GeneratedAnswer` construction, citations, sections, and reference-note assembly
  - `intent/compound_question_limitation_resolver.py`
    - owns deterministic compound-question limitation detection
- `src/shared/formatting/ingestion_result_formatter.py`
  - exposes runtime-profile diagnostics in human and JSON output
- `src/infrastructure/retrieval/keyword/scoring/`
  - `sql_keyword_scoring_config.py`
    - owns scorer config loading and marker tables
  - `sql_keyword_morphology.py`
    - owns morphology expansion and section-path variant matching
  - `sql_keyword_text_helpers.py`
    - owns section-path parsing and ordered-query helper logic
  - `sql_keyword_penalties.py`
    - owns chunk-role and noise penalty rules
  - `sql_keyword_score_components.py`
    - owns identifier/section match state and scorer metadata assembly
- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py`
  - reduced to score orchestration and total-score assembly
- `src/infrastructure/db/repositories/retrieval/sql_keyword_repository.py`
  - now imports morphology expansion from the dedicated scoring module
- `tests/unit/infrastructure/retrieval/keyword/`
  - updated to import moved morphology helpers directly instead of through the scorer file

Still open inside Phase 0:

- continue shrinking `IngestionWorkflow` itself
  - ownership is improved, but the coordinator is still a large hotspot and should be reduced further in a later slice
- continue removing broad fallback behavior from low-level parser/runtime defaults where silent drift still exists

### Phase 1 - Strengthen Parsing And Table Contracts

Goals:

- make upstream structure more trustworthy and easier for downstream layers to consume

Actions:

- keep hardening table reconstruction in `src/application/workflows/parsing/tables/`
- formalize one stable parsed-table contract for downstream consumers:
  - family identity
  - stream ownership
  - header paths
  - axis summary
  - typed row projections
  - structure quality
- isolate report/debug observers from core parsing workflow execution
- make OCR strategy an explicit resolved decision object per document run

### Phase 2 - Tighten Retrieval Intent And Evidence-Family Selection

Goals:

- stop wrong evidence families from reaching answer generation

Actions:

- refine `RetrievalQueryChunkTypePreferenceMapper`
- refine `IntentChunkTypeScorer`
- refine `TableFocusedEvidencePruner`
- add explicit family rejection rules for focused table and identifier questions
- surface ranking-feature diagnostics per candidate for auditing

Success criterion:

- focused questions should carry fewer but more relevant chunks
- context budget should be spent on direct evidence first

### Phase 3 - Bridge Identifier And Table Answers Properly

Goals:

- make identifier and list-style answers consume structured tables directly

Actions:

- extend `IdentifierAnswerRenderer` to consume `AnswerTable` when structured row evidence exists
- add generic identifier extraction from typed table rows
- avoid dependence on extraction persistence alone for identifier QA
- unify table-driven answer logic across:
  - spare parts
  - maintenance schedules
  - troubleshooting tables
  - identifier tables
  - specification tables

Success criterion:

- if a value exists only in a hydrated table row, the answer path can still use it deterministically

### Phase 4 - Make Semantic Enrichment A First-Class Optional Layer

Goals:

- support clean structural-only and structural-plus-semantic runtimes

Actions:

- define explicit semantic-enrichment mode in ingestion and QA
- keep structural ingestion fully valid without extraction
- make semantic retrieval clearly degrade when extraction is unavailable, without pretending it is present
- modernize extraction planning away from a combined-prompt-centered mental model
- let extraction families evolve independently

Success criterion:

- operators can intentionally choose:
  - fast structural ingest
  - full semantic ingest
- downstream services know which mode they are running in

### Phase 5 - Rebuild The Prompt Boundary Around Typed Evidence

Goals:

- stop turning rich evidence back into prompt noise

Actions:

- preserve `StructuredAnswerContext` as the core answer evidence model
- redesign generic answer prompting so structured evidence becomes primary
- keep raw chunk prose and appendix evidence explicitly secondary
- reduce duplication across:
  - sources
  - tables
  - key-values
  - structured entities
  - relationship summaries

Success criterion:

- better parsing and retrieval should produce cleaner prompts, not larger noisier prompts

### Phase 6 - Simplify Retrieval Ranking And Observability

Goals:

- make ranking more maintainable and tunable

Actions:

- decompose keyword ranking into explicit feature modules
- emit feature diagnostics for benchmark and debug tools
- separate structural table signals from generic lexical signals
- keep reranker behavior auditable

Success criterion:

- retrieval regressions become traceable by feature, not just by final score

### Phase 7 - Operational Profiles, Performance, And Concurrency

Goals:

- make the system predictable in dev, benchmark, and production modes

Actions:

- formalize Qdrant local versus server runtime profiles
- make single-process limitations explicit in local mode
- expose profile-level guidance for:
  - OCR cost
  - extraction cost
  - embedding cost
  - answer-generation cost
- reduce mixed production/debug code paths

Success criterion:

- developers and operators can reason about cost, speed, and concurrency without hidden coupling

### Phase 8 - Unified Evaluation Gates

Goals:

- make improvements measurable across unseen document families

Actions:

- unify parsing, retrieval, and answering quality gates
- verify both structural-only and semantic-enriched modes
- require generic test cases for:
  - manuals
  - certificates
  - drawings
  - reports
  - datasheets
- prefer family-level and structure-level assertions over current-document assertions

Success criterion:

- the system can be hardened against new document families without tuning only to the current database

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
9. Phase 8

Why this order:

- parsing and structure quality must improve before retrieval can be simplified
- retrieval family selection must tighten before answer generation can become cleaner
- semantic enrichment should be formalized after structural paths are trustworthy
- prompt-boundary cleanup is most valuable once upstream evidence is stable

## Immediate High-Value Next Slice

If the team wants the highest-impact generic slice next, the best order is:

1. tighten table and identifier retrieval-family pruning
2. make identifier answers consume `AnswerTable` directly
3. split the biggest orchestration hotspots

That slice is generic, high-impact, and does not depend on the current sample corpus.

## Final Verdict

The system is no longer a weak prototype. It has many of the right enterprise building blocks.

But it is still not yet a top-tier enterprise technical-document RAG system for unseen documents at scale.

The main remaining issue is not missing capability. It is uneven maturity between:

- structure extraction
- semantic enrichment
- retrieval-family control
- answer evidence consumption
- orchestration ownership

The path to excellence is now clear and generic:

- make parsing and table contracts stronger
- tighten retrieval evidence-family selection
- let deterministic answer paths consume structured tables directly
- separate structural mode from semantic-enrichment mode
- split orchestration hotspots into real stage-owned units

That is the most scalable, maintainable, and document-agnostic path forward.
