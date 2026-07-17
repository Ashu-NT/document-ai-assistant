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
- this document was cross-checked directly against the real database (`data/maintenance_ai.db`, 36
  documents, no LLM calls) as of the "Empirically-Verified Weaknesses" section below - several findings
  there were only visible in real data, not in code review or the existing unit-test suite

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

- `src/application/workflows/ingestion/ingestion_workflow.py` - 290 LOC after Phase 0 refactor
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

- `ParsingWorkflow` still coordinates parsing, normalization, OCR enrichment, page fallback OCR, and validation directly
- parser input limits are now resolved explicitly at composition time, but OCR strategy is still split across policy and runtime-factory layers
- debug/report generation is now outside the active production parsing workflow path, but there is not yet one explicit optional observer contract for parse-time diagnostics

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

### 10. RESOLVED - Retrieval ranking was concentrated in one scorer

Relevant files:

- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py`
- `src/infrastructure/retrieval/keyword/scoring/`
- `src/infrastructure/retrieval/rerankers/deterministic/`

Status update (verified directly against current code, not just the Phase 0 status list below):

- `sql_keyword_scorer.py` is now 195 LOC and reduced to score orchestration and total-score assembly only
- feature calculation, weighting, and penalty logic have been decomposed into `scoring/sql_keyword_scoring_config.py`, `sql_keyword_morphology.py`, `sql_keyword_text_helpers.py`, `sql_keyword_penalties.py`, and `sql_keyword_score_components.py`
- this item was stale relative to this document's own Phase 0 "implemented slice" list - it described a problem the same work session had already fixed

Remaining, narrower gap (this is now a Phase 6 concern, not a Phase 0/architecture one):

- feature diagnostics are not yet surfaced per-candidate for benchmark/debug tooling, so regression diagnosis is still slower than it should be
- see Phase 6

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

## Empirically-Verified Weaknesses (Real Corpus, DB-Verified)

Everything above this section was found by reading code and architecture. The items below were found a
different way: querying `data/maintenance_ai.db` directly with SQL, against the real ingested corpus (36
documents - manuals, certificates, datasheets, reports, drawings - spanning multiple languages), with no
LLM calls involved. This matters because code-level review can miss failure modes that only show up in
real data at scale. None of the corpus's specific documents are referenced as targets to fix for - per this
plan's own document-agnostic constraint, the failure classes below (not the sample documents) are what
should drive the fix.

### 14. RESOLVED - Chunk-size enforcement failed on real documents

Root cause found and fixed: `TableFragmentSplitter.split()`'s single-group branch (the case where the
row-grouping loop decides all rows fit under the token budget) returned the fragment with its *original,
pre-split* `text`/`token_count` completely untouched - only `table_rows`/`table_row_start`/`table_row_end`
were replaced. The multi-group branch already re-rendered `text`/`token_count` from the actual grouped rows;
the single-group branch did not. So whatever bloat existed in the original fragment's text (built upstream,
before row-based cleanup/whitespace normalization) sailed through completely unbounded, regardless of what
the size check determined about the cleaned rows. Reproduced directly (a fragment with a 100,000-token
stale original text but small actual rows was returned with the full 100,000-token text intact) and fixed by
re-rendering `text`/`token_count` from the grouped rows in the single-group branch too, mirroring the
multi-group branch's existing pattern. New regression test added
(`test_table_fragment_splitter_rerenders_text_when_all_rows_fit_in_one_group`) - the prior test suite only
ever exercised the multi-group path, which is why this went unnoticed. Full unit suite verified green aside
from 2 pre-existing, unrelated failures (confirmed via `git stash` that both fail identically without this
fix applied: an OCR-fallback wiring test and a `TableAsset.to_structured_row_text` missing-attribute error in
`scripts/export_document_table_assets.py`, both from unrelated in-progress work elsewhere in the repo).

Evidence (original finding, kept for reference):

- 25 chunks in the real corpus exceed 2,000 estimated tokens; the worst is 11,766 tokens in one chunk
  (`PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf`), against a configured 200-1,000 token profile limit
- affects 4 distinct real documents (`PURO 30`, `002878 - MY Cosmos - Full System Manual`,
  `SOFTENER 9500`, `System Manual PB-06175`)
- every oversized chunk found has a `table_category` set - all are table-derived, and the largest come
  from complex engineering-drawing BOM/wiring tables
- confirmed this is not accidentally fixed by the newest `ingestion_input_limits.py` work: that module only
  resolves file-size/page-count acceptance limits, not chunk-token limits, and is a completely separate
  concern from `TableFragmentSplitter`/`ChunkTextSplitter`

Why this matters:

- an 11,766-token chunk either gets truncated by the LLM's context window or crowds out every other piece
  of retrieved evidence for that query - this directly destroys answer quality for whatever document it
  belongs to
- root cause is still unconfirmed - needs to be traced through `TableFragmentSplitter`/logical-table-family
  composition to find why row-level splitting isn't firing for these specific tables

### 15. Certification-table classification has near-zero recall on real certificate documents

Evidence:

- of the 7 real `document_type='certificate'` documents in the corpus, zero of their 49 real table chunks
  are classified `certification_table` - all 19 real `certification_table` hits corpus-wide come from
  `manual`-type documents' embedded appendices, not from standalone certificates
- real certificate content pulled directly from the DB is often bilingual German/English ("Zertifikat",
  "Kalibriernummer", "Spezifikation/specification | Soll/nominal | Ist/result") - the classifier's
  certification vocabulary (`approval, atex, certificate, class, conformity, iecex, particulars`) is
  English-only

Why this matters:

- this is a sharper, quantified version of weakness #4 (table understanding not consumed consistently) -
  the classifier is not even reaching the right category for an entire, common, non-English document family
- confirms this plan's own scope requirement (generalize across unseen manuals/certificates/drawings/
  reports/datasheets) is not yet met for non-English certificates

### 16. Text encoding corruption reaches retrieved chunk content, and is not limited to one language

Evidence:

- real extracted content includes replacement characters and spaceless garbled runs, e.g.
  `"Eswird bstii dasssPrfgebis ausPrfunnanderLifrung selst..."` (a mangled German/English test-certificate
  sentence) and encoding artifacts like `"L�rssen-Kr�ger"` (should be "Lürssen-Krüger")
- not isolated to the bilingual certificates above - the same corruption pattern appears in English-language
  manuals too (`SOFTENER 9500-OWNERS MANUAL`, `PURO 30-OWNERS MANUAL`, `TD_28022101_Rev-A.pdf`)

Why this matters:

- a chunk this garbled is close to useless if retrieved - an LLM cannot reliably extract meaning from it -
  and it can still score well enough on keyword/identifier matches to be retrieved anyway
- likely a font-encoding/glyph-mapping issue in specific source PDFs rather than a single parsing bug; needs
  its own root-cause pass, likely in the Docling text-extraction/normalization layer

### 17. Over half of all classified tables fall into the general_table catch-all

Evidence:

- 1,129 of 2,012 real table chunks with a `table_category` set (56%) are `general_table`
- this is a corpus-wide number, not a cherry-picked example, and quantifies what weakness #4 only stated
  qualitatively

Why this matters:

- real-world classifier recall across the specific categories (spare parts, technical data, operating
  limits, troubleshooting, etc.) is meaningfully weaker in practice than the curated unit-test suite's
  examples suggest
- this is exactly the kind of drift a purely code-level or unit-test-level review cannot see

### 18. A real document is currently, actively failing ingestion - not a hypothetical OCR gap

Evidence:

- `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf` has 3 failed ingestion runs in
  `ingestion_runs`, the most recent from the day this finding was made, all with the identical error
  `"Post-classification chunk finalization produced zero chunks for a non-empty parsed document."`
- its 4 parsed elements are all `picture` type with `text=None` - a scanned document where OCR extracted
  nothing usable
- the failure is not silent at the ingestion-run level - `IngestionWorkflow._ensure_final_graph_has_chunks`
  raises a structured `IngestionWorkflowError` (`error_code="ingestion.final_graph.no_chunks"`) and the run
  is correctly marked `status='failed'` - but retrying 3 times produced the identical failure each time, so
  the underlying OCR gap is not self-healing
- this is the same failure class weakness #3 (OCR runtime model) describes, now confirmed as a live,
  reproducible, currently-unresolved case rather than a theoretical one

Why this matters:

- the document exists in the `documents` table space but has no usable content and a failed ingestion run -
  worth confirming the retrieval/QA layer actually checks ingestion-run status before answering questions
  scoped to a document like this, rather than silently returning "no information found"

## Resolved This Session (Not Yet Reflected Elsewhere In This Document)

The following were found and fixed in a parallel review session, working from the same principle this plan
states directly: RAG quality is capped by parse and retrieved-chunk quality. Listed here so this document
stays the single source of truth and this work is not accidentally redone or reverted:

- **TOC misclassification**: `TableSemanticClassifier`'s bare `"contents"` substring check was scoped from
  the table's full body/caption text down to the section-heading path only - a spec table mentioning
  "oil contents"/"tank contents" no longer misfiles as `TOC_TABLE`
- **Certification-vs-operating-limits ordering**: `looks_like_certification_table` is now checked before
  `looks_like_operating_limits_table`/`looks_like_technical_data_table` in `classify()` - a real ATEX/IECEx
  certification table with environmental-limit rows no longer gets stolen by the generic operating-limits
  rule (verified live against a realistic repro before and after)
- **Chunk-type preservation gap**: `ChunkTypeResolver`'s standalone-preserved-type set now includes
  `MAINTENANCE_INTERVAL`, `TROUBLESHOOTING`, and `OPERATION_INSTRUCTION` alongside the pre-existing
  `TECHNICAL_SPECIFICATION`/`CERTIFICATION_INFO` - table-category-derived chunks in these three families
  can no longer be silently re-scored down to `GENERAL` by keyword-signal scoring
- **Structured-entity fallback gap**: `StructuredEvidenceResolver`/`RetrieveStructuredEntitiesTool` now fall
  back to a full document-scoped list for `SPARE_PART`/`SPECIFICATION` when free-text search matches
  nothing (previously only troubleshooting/maintenance/procedure/safety had this) - directly improves
  "list the spare parts"/"what is the specification of X" style questions
- **Multi-column reading-order gap**: `DoclingDocumentNormalizer` now reorders same-page elements into
  correct left-column-then-right-column order when the page layout analyzer detects genuine 2-column
  content, using the previously-computed-but-unused `layout_page_order` metadata - single-column pages
  (the large majority) are untouched
- **`TableFocusedEvidencePruner` over-deletion**: this is the *other* half of weakness #5 (not the "doesn't
  suppress mismatched families" half, which is still open) - the pruner no longer treats
  `chunk_type in {OVERVIEW, GENERAL}` alone as a low-value signal; it now relies solely on the
  auto-generated-scaffolding-prefix check (`"Context: "`/`"Section overview: "`), so real content that
  merely fell into the `GENERAL` catch-all (a caveat, a safety note) is no longer discarded on
  table-focused queries

Still open and not yet touched by this parallel session: `TableSignalCollector`'s `detect_signals()` does
not apply the same spare-parts/spec-matrix disambiguation `classify()` gained above - a table `classify()`
correctly demotes to `TECHNICAL_DATA_TABLE` can still carry a stale `spare_parts` signal tag in persisted
metadata. No downstream consumer reads `TableSignal` for routing yet, so this has no live user-facing
impact today, but it is incorrect persisted metadata.

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
  - `IngestionWorkflow` now delegates ingestion-run persistence, duplicate early exits, and failure finalization to dedicated pipeline helpers
  - `IngestionWorkflow` now delegates run bootstrap concerns (path resolution, file hashing, context resolution, `IngestionRun` creation, started-event emission, and initial progress emission) to a dedicated bootstrap helper
  - `IngestionWorkflow` now delegates duplicate-stage orchestration and success completion/final event emission to dedicated pipeline coordinators
  - `IngestionWorkflow` now delegates stage status/start/completed lifecycle plumbing and stage event-payload assembly to dedicated ingestion pipeline collaborators
- `IngestionWorkflow` now delegates per-stage `IngestionRun` metadata/state mutation to a dedicated state applier
- `IngestionWorkflow` now delegates internal collaborator assembly to a dedicated pipeline builder and delegates the full parse/register/classify/finalize/extract/embed/index/quality stage sequence to a dedicated sequence executor
- `AnswerGenerationService` now delegates settings resolution, prompt execution/retry, result assembly, and compound-question limitation handling to dedicated collaborators
- `SqlKeywordScorer` now delegates morphology helpers, scoring config, penalties, and score-component assembly to grouped scoring modules
- parser file-size and page-count limits are now resolved explicitly in the orchestrator layer instead of failing open inside `DoclingParser` or `IngestionRequestValidator`
- parsing chunking settings are now resolved explicitly in the orchestrator layer instead of failing open inside `DocumentGraphBuilder`
- debug/profile parser entrypoints now consume the same shared input-limit resolver as the production parsing runtime

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
  - resolves explicit ingestion input limits for request validation
- `src/application/orchestrator/ingestion/ingestion_input_limits.py`
  - owns explicit file-size and page-count limit resolution for parsing and ingestion validation
- `src/application/orchestrator/ingestion/parsing_chunking_settings.py`
  - owns explicit chunk-size, overlap, and minimum-section-text resolution for production and debug parsing entrypoints
- `src/application/workflows/ingestion/ingestion_workflow.py`
  - consumes resolved capabilities and blocks implicit semantic-linking drift
  - delegates parsing, registration, classification, finalization, extraction, and vector-indexing clusters to stage-owned collaborators
- `src/application/workflows/ingestion/pipeline/extraction_retry_step.py`
  - uses the same resolved runtime capabilities during extraction retry
- `src/application/workflows/ingestion/pipeline/`
  - `ingestion_duplicate_coordinator.py`
    - owns file-hash/content-hash duplicate gate orchestration and duplicate short-circuit coordination
  - `ingestion_run_bootstrap.py`
    - owns file-path resolution, hash computation, context resolution, `IngestionRun` creation, started-event emission, and initial progress emission
  - `ingestion_run_store.py`
    - owns ingestion-run create/update/status persistence
  - `ingestion_stage_lifecycle_coordinator.py`
    - owns stage session context plus repeated status/start/completed stage lifecycle coordination
  - `ingestion_stage_payload_builder.py`
    - owns stage-completed payload assembly for parsing, classification, finalization, extraction, and vector stages
  - `ingestion_stage_sequence_executor.py`
    - owns top-level stage-sequence orchestration and exception-to-failed-run routing
  - `ingestion_stage_state_applier.py`
    - owns `IngestionRun` field mutation after parsing, classification, finalization, and embedding stage results
  - `ingestion_success_finalizer.py`
    - owns run completion status persistence, success result assembly, completed-event emission, and terminal progress emission
  - `ingestion_workflow_pipeline.py`
    - owns internal ingestion pipeline collaborator assembly so `IngestionWorkflow` no longer constructs every helper inline
  - `duplicate_ingestion_exit_handler.py`
    - owns duplicate skip result assembly and skipped-duplicate event emission
  - `sequence/`
    - `document_structure_stage_sequence.py`
      - owns registration, classification, and finalization stage sequencing
    - `semantic_index_stage_sequence.py`
      - owns extraction, embedding, indexing, and optional quality stage sequencing
  - `ingestion_exception_handler.py`
    - owns rollback, failed-run persistence, failed-event emission, and workflow-error wrapping
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
- `src/infrastructure/parsing/docling/docling_parser.py`
  - no longer loads ingestion settings or silently falls back to effectively-unbounded parser limits
- `src/application/workflows/parsing/builders/document_graph_builder.py`
  - no longer loads ingestion settings or silently falls back while resolving chunk-size/overlap thresholds
- `src/application/validation/ingestion/ingestion_request_validator.py`
  - no longer fails open to an effectively-unbounded file-size limit when settings resolution drifts
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
  - the primary workflow coordinator is now under the repo file-size target and no longer owns the full stage sequence inline
  - the next safe ingestion-oriented cleanup is optional follow-up work around specialized retry paths such as `ExtractionRetryStep`, not the main happy-path workflow
- audit remaining generic `resolve_setting()` fail-open usages in non-ingestion runtime code and decide which ones should become explicit composition-time failures instead of permissive defaults

### Phase 1 - Strengthen Parsing And Table Contracts

Status:

- in progress
- implemented slice:
  - `ParsingWorkflow` no longer imports parsing/chunking/quality report writers or performs workflow-level debug report side effects
  - active debug parsing/report generation remains script-owned, which is a cleaner separation than production-workflow-owned report writing
  - production, debug, and profiling parsing entrypoints now share the same explicit parser/chunking settings resolution instead of each low-level component importing settings on its own

Goals:

- make upstream structure more trustworthy and easier for downstream layers to consume

Actions:

- highest priority, added from DB-verified evidence (weakness #14): find and fix why some tables
  (confirmed: complex engineering-drawing BOM/wiring tables) bypass `TableFragmentSplitter`/
  `ChunkTextSplitter` token limits entirely - real chunks up to 11,766 tokens exist against a
  200-1,000 token configured limit
- added from DB-verified evidence (weakness #15): broaden `TableSpecificationRuleEvaluator`'s
  certification vocabulary beyond English-only markers, or add a document-type/language-aware signal -
  real certificate documents in this corpus are frequently bilingual and are not being classified as
  certification tables at all
- added from DB-verified evidence (weakness #16): root-cause text-encoding corruption in extracted
  chunk content (replacement characters, spaceless garbled runs) - affects both bilingual and
  English-only real documents, likely a font/glyph-mapping issue in Docling text extraction
- added from DB-verified evidence (weakness #17): track the `general_table` fallback rate as an explicit
  metric (currently 56% of all real classified tables) and treat reducing it as a concrete success
  criterion for table-contract hardening, not just qualitative improvement
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
- added from DB-verified evidence (weakness #18): confirm the retrieval/QA layer checks ingestion-run
  status before answering questions scoped to a document with a `status='failed'` run, rather than
  silently returning "no information found"

### Phase 2 - Tighten Retrieval Intent And Evidence-Family Selection

Status update:

- `TableFocusedEvidencePruner`'s over-deletion half is resolved (see "Resolved This Session" above) - it no
  longer discards real `GENERAL`/`OVERVIEW` content based on chunk_type alone, only on the recognized
  auto-generated-scaffolding-prefix signal
- the other half of the original weakness (#5) is still fully open: the pruner does not yet suppress
  mismatched-but-still-"direct evidence" table families (e.g. an unrelated maintenance-interval table
  surviving alongside the correct spare-parts table for a spare-parts-focused query)

Goals:

- stop wrong evidence families from reaching answer generation

Actions:

- refine `RetrievalQueryChunkTypePreferenceMapper`
- refine `IntentChunkTypeScorer`
- extend `TableFocusedEvidencePruner` with family-mismatch rejection (the still-open half above) - do not
  revert or bypass the scaffolding-prefix-only logic already landed this session
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

Updated after DB-verified evidence (weakness #14): the highest-impact generic slice next is

1. fix chunk-size enforcement for table-derived chunks (weakness #14) - this is actively producing
   multi-thousand-token chunks in the real corpus right now, ahead of anything else in this list
2. tighten table and identifier retrieval-family pruning (remaining half of weakness #5)
3. make identifier answers consume `AnswerTable` directly
4. split the biggest orchestration hotspots

That slice is generic, high-impact, and does not depend on the current sample corpus - item 1 is a defect
class (oversized chunks from complex tables), not a fix tailored to any one document.

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
