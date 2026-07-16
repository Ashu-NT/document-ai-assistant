# Table Answering, Retrieval, and Structure Findings

## Scope

This report was written after scanning the current parsing, table, retrieval, and answer-generation code paths related to these observed issues:

- table row normalization is still too weak
- answer generation is not consistently extracting exact structured facts from hydrated table evidence
- retrieval still admits some low-value same-intent chunks that pollute final answers for table questions
- local Qdrant is single-process only, so live QA checks need to be run sequentially

This is a findings-first report. No implementation changes are proposed here until after the discovered behavior is explained.

## Executive Summary

The current system already has a stronger table pipeline than the runtime answers suggest.

At parsing time, the codebase already captures:

- logical table families across pages
- page layout lanes and regions
- table categories
- table shapes
- header paths
- axis summaries
- structured rows

The main problem is not lack of raw structure. The main problem is that the strongest structure is only partially exploited after retrieval.

The current weaknesses are concentrated in four layers:

1. parsing normalization is still specialized for only a few table families
2. answer-time prompt/context projection weakens or caps structured table evidence too early
3. deterministic answer renderers do not consistently consume the best structured table representation
4. retrieval and context expansion still allow lower-value same-intent chunks to travel with high-value table evidence

The local Qdrant issue is real, but it is an operational constraint, not the main answer-quality defect.

## What The Current Code Already Does Well

### 1. Parsing already builds rich table structure

Key files:

- `src/domain/assets/table_asset.py`
- `src/application/workflows/parsing/tables/table_semantic_resolver.py`
- `src/application/workflows/parsing/tables/logical_table_family_resolver.py`
- `src/application/workflows/parsing/layout/page_layout_analyzer.py`

Current strengths:

- `TableAsset` stores `rows`, `parallel_stream_rows`, `cell_spans`, `header_paths`, `axis_summary`, `table_shape`, `table_category`, `logical_table_family_id`, `continuation_role`, and related metadata.
- `LogicalTableFamilyResolver` already merges compatible physical tables into logical families and uses page adjacency plus layout compatibility.
- `PageLayoutAnalyzer` already computes orientation, regions, lane counts, lane indexes, and front-matter status.
- `TableSemanticResolver` already classifies tables and writes normalized structure metadata back into parser metadata.

Conclusion:

The parsing layer is not primitive. It is already doing meaningful layout-aware and family-aware reconstruction.

### 2. Retrieved chunks can be hydrated back into richer table evidence

Key file:

- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`

Current strengths:

- retrieved table-like chunks are rehydrated from the stored `DocumentGraph`
- logical table family members are merged
- merged rows are written into `table_rows_json`
- header paths and axis summary are preserved in chunk metadata
- hydrated chunk content contains structure context, original markdown, and rendered structured rows

Conclusion:

The QA path is not limited to raw chunk text. It already has access to richer table evidence.

### 3. The answer pipeline already has structured context objects

Key files:

- `src/application/workflows/question_answering/answer_context/answer_context_organizer.py`
- `src/application/workflows/question_answering/answer_context/models/structured_answer_context.py`
- `src/application/workflows/question_answering/answer_context/structured_source_builder.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`

Current strengths:

- `StructuredAnswerContext` carries sources, tables, source groups, section groups, key-values, maintenance entries, and structured entities
- `StructuredSourceBuilder` decodes table rows, header paths, and axis summary from retrieved chunk metadata
- `AnswerTableProjector` routes different table kinds into specialized projection builders

Conclusion:

The system already has a strong in-memory structured evidence model. The main gap is how consistently that structure is exploited downstream.

## Findings

## 1. Parsing-time row normalization still needs broader real-world coverage

Primary files:

- `src/application/workflows/parsing/tables/normalization/table_row_semantic_normalizer.py`
- `src/domain/assets/table_rows/spare_parts_table_normalizer.py`
- `src/domain/assets/table_rows/troubleshooting_table_normalizer.py`

What is happening now:

- `TableRowSemanticNormalizer` already delegates to:
  - `SparePartsTableNormalizer`
  - `TroubleshootingTableNormalizer`
  - `MaintenanceScheduleTableNormalizer`
  - `SpecificationKeyValueTableNormalizer`
  - `CertificationParticularsTableNormalizer`
  - `GenericWrappedRowTableNormalizer`
- this is better than earlier snapshots, but broad real-world table coverage still depends on how well those generic normalizers reconstruct multi-line and matrix-heavy layouts

Why this matters:

- maintenance schedule tables
- certification particulars tables
- specification matrices
- operating limits tables
- general key-value tables
- multi-line matrix-style tables

still depend mostly on later answer-time heuristics instead of being normalized once at parsing time.

Observed architectural consequence:

- the parser has rich table storage, but generic row semantics are under-normalized
- the burden shifts downstream to answer renderers and prompt serializers
- this increases duplication of logic and inconsistent behavior by question type

Bottom line:

The normalization layer is materially stronger than before, but it still needs more robust row/continuation reconstruction for wide operational tables and difficult maintenance/troubleshooting matrices.

## 2. Prompt-time table projection diverges from answer-time table projection

Primary files:

- `src/application/prompts/answer_generation/prompt_context/tables/prompt_table_projector.py`
- `src/application/prompts/answer_generation/prompt_context/tables/prompt_table_row_normalizer.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`

What is happening now:

- `AnswerTableProjector` uses the stronger answer-context projection stack
- `PromptTableProjector` uses a much simpler `PromptTableRowNormalizer`
- `PromptTableRowNormalizer` only:
  - strips empty cells
  - guesses whether row 0 is a header
  - maps cells by header position

Why this matters:

The generic LLM prompt path is receiving a weaker table abstraction than the deterministic answer path.

That means:

- deterministic renderers may see better typed rows than the LLM prompt serializer
- the generic LLM can still receive tables in a flattened or weakly typed form
- answer quality depends too much on which renderer path gets selected

Bottom line:

There are effectively two table-projection qualities in the codebase right now:

- stronger answer-time table projection
- weaker prompt-time table projection

That divergence is a core consistency problem.

## Implementation Focus For This Pass

The current implementation pass should stay tightly scoped to the highest-value shared fixes:

1. Route prompt-time table projection through the already-built `StructuredAnswerContext.tables` path first, and only fall back to raw-source table projection when typed tables are missing.
2. Reuse a single prompt-table label mapper so prompt labels do not fork across two code paths.
3. Add a deterministic maintenance-table fallback renderer that uses `MaintenanceTableCandidateExtractor` directly when `maintenance_entries` are absent or incomplete.
4. Keep old source-based prompt table projection only as a compatibility fallback, not the active path.
5. Cover the new path with prompt projector, serializer, and deterministic renderer tests before expanding into broader retrieval filtering work.

## 3. Structured context exists in Python, but the prompt boundary still weakens it

Primary files:

- `src/application/prompts/answer_generation/answer_prompt_builder.py`
- `src/application/prompts/answer_generation/prompt_context/projectors/prompt_context_projector.py`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py`
- `src/application/prompts/answer_generation/prompt_context/appendix/raw_source_appendix_formatter.py`

What is happening now:

- `AnswerPromptBuilder` builds:
  - evidence schema text
  - structured evidence JSON payload
  - raw source appendix text
- `StructuredEvidencePayloadSerializer` caps every structured array to 20 items
- raw appendix remains prose-heavy
- `PromptContextProjector` preserves some structure, but prompt delivery still mixes:
  - structured JSON
  - raw source text
  - capped bundles

Important observed gap:

`StructuredEvidencePayloadSerializer._source_payload()` includes:

- source metadata
- content
- identifiers
- table shape
- header paths
- axis summary

but it does not include `table_rows` in the source payload itself.

The serializer does include `tables`, but that creates a split representation:

- source content says one thing
- tables array says another
- appendix prose says another

This increases prompt duplication and weakens source-to-table locality for the model.

Bottom line:

The system has structured evidence, but the generic LLM still receives a mixed prompt where structure is present yet not consistently centered.

## 4. Deterministic answer renderers are useful, but they are too dependent on partial typed extractions

Primary files:

- `src/application/services/answer_generation/answer_generation_service.py`
- `src/application/services/answer_generation/formatting/renderers/maintenance_schedule_renderer.py`
- `src/application/services/answer_generation/formatting/renderers/troubleshooting_renderer.py`
- `src/application/services/answer_generation/formatting/renderers/deterministic_answer_renderer_dispatcher.py`

What is happening now:

- the dispatcher prefers deterministic renderers before the LLM path
- this is good when the typed evidence is correct
- it is weak when typed evidence is incomplete or over-merged

Example structural issue:

- `MaintenanceScheduleRenderer` renders from `maintenance_entries`
- if maintenance entry extraction is incomplete, noisy, or over-merged, the answer degrades even when hydrated tables are present
- it does not use a stronger table-first recovery path before giving up

Example brittleness:

- `TroubleshootingRenderer` assumes a clean `Symptom` / `Cause` / `Remedy` shape
- that works only when earlier row normalization succeeded strongly

Bottom line:

The deterministic layer is useful, but it is not yet robust enough to treat normalized table evidence as the primary fact source across all table-heavy answer types.

## 5. Retrieval still allows low-value same-intent chunks to travel with high-value table evidence

Primary files:

- `src/application/services/retrieval/hybrid_retrieval_service.py`
- `src/infrastructure/retrieval/rerankers/deterministic/deterministic_hybrid_reranker.py`
- `src/application/workflows/retrieval/deduplication/retrieved_chunk_deduplicator.py`
- `src/application/workflows/retrieval/retrieval_workflow.py`
- `src/application/workflows/retrieval/retrieval_context_expander.py`

What is happening now:

- hybrid retrieval fuses dense, SQL/keyword, and structured evidence
- reranking adds:
  - identifier matches
  - chunk role
  - intent/chunk-type fit
  - section-path hits
  - noise penalties
- deduplication removes exact and companion duplicates
- context expansion adds nearby/related chunks after retrieval

What is still missing:

- no table-family-first pruning step before answer generation
- no strong rule that says:
  - when a direct hydrated table family exists for a table question,
  - overview/context/general same-intent companions must be aggressively demoted or dropped

Result:

- the right table chunk is often present
- but lower-value chunks with the same broad intent still survive into answer generation
- those chunks pollute the final answer, especially on maintenance, troubleshooting, and spare-parts questions

Bottom line:

The retrieval stack is not broken, but it is still too permissive for table-centric question answering.

## 6. Layout awareness is strong in parsing, but underused after retrieval

Primary files:

- `src/application/workflows/parsing/layout/page_layout_analyzer.py`
- `src/application/workflows/parsing/tables/logical_table_family_resolver.py`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/question_answering/answer_context/structured_source_builder.py`

What is happening now:

- layout region and lane metadata are used in parsing/family resolution
- but downstream answer context does not appear to carry layout region/lane/orientation as first-class prompt evidence

Why this matters:

For:

- two-column TOCs
- parallel tables
- wide landscape specification tables
- page-local left/right structures

the parsing layer understands more than the answer layer currently uses.

Bottom line:

The system already pays the cost to compute layout intelligence, but not enough of that intelligence survives into retrieval-aware answer generation.

## 7. Local Qdrant is an operational constraint, not a retrieval-quality defect

Primary file:

- `src/application/orchestrator/ingestion/vector_runtime_builder.py`

What is happening now:

- local mode uses `QdrantClient(path=str(qdrant_settings.storage_path))`
- this is file-backed local Qdrant
- it is suitable for local development, not for concurrent multi-process QA probing

Operational consequence:

- live QA checks must be sequential when local mode is active
- parallel debug scripts or multiple active clients can conflict

Bottom line:

This should be treated as a dev-runtime constraint. It is not the main reason answer quality is weak.

## 8. The current tests are good at unit behavior, but weaker at multi-layer table-answering realism

Evidence from the test map:

- there are unit tests for:
  - spare-parts normalization
  - troubleshooting normalization
  - table evidence hydration
  - answer table projection
  - prompt context projection
  - structured evidence payload serialization
  - reranking
  - deduplication

What appears missing or light:

- answer-quality integration tests where:
  - retrieved chunk -> hydrated family -> structured context -> deterministic answer
  - or retrieved chunk -> prompt bundle -> generic LLM request shape
- regression tests asserting:
  - direct table evidence outranks same-intent narrative noise for table questions
  - maintenance answers prefer hydrated schedule tables over weaker maintenance prose
  - prompt serializer preserves enough structure for exact fact extraction

Bottom line:

The code has many unit tests, but the current failures are mostly cross-layer behavior problems.

## Root-Cause Summary

The biggest current quality gaps are not caused by one broken module.

They come from a mismatch between layers:

1. parsing already knows a lot about tables
2. retrieval usually finds useful evidence
3. answer generation still does not consistently privilege the best structured representation of that evidence

So the main defect is not “missing table handling”.

The main defect is “insufficient end-to-end exploitation of the table handling that already exists”.

## Implementation Plan

## Phase 1. Strengthen generic parsing-time table normalization

Goal:

Move more semantic table normalization earlier into the parsing layer so later answer logic has better inputs.

Target area:

- `src/application/workflows/parsing/tables/normalization/`
- `src/domain/assets/table_rows/`

Changes:

- extend `TableRowSemanticNormalizer` into a pluggable chain rather than a two-normalizer gate
- add generic normalizers for:
  - maintenance schedule / interval tables
  - specification / key-value tables
  - certification particulars tables
  - generic wrapped-row structured tables
- keep them semantic, not document-specific
- use:
  - header paths
  - axis summary
  - row continuity
  - cell spans
  - logical table family continuity

Do not:

- hardcode current database document labels or benchmark-only column names

Expected outcome:

- more table families become normalized once at parsing time
- less answer-type-specific repair later

## Phase 2. Unify prompt-time and answer-time table projection quality

Goal:

Stop the generic LLM prompt path from receiving a weaker table abstraction than the deterministic renderer path.

Target area:

- `src/application/prompts/answer_generation/prompt_context/tables/`
- `src/application/workflows/question_answering/answer_context/tables/`

Changes:

- either reuse the stronger `AnswerTableProjector` logic in prompt projection
- or create a shared lower-level table projection core used by both
- remove the current quality split between:
  - `PromptTableRowNormalizer`
  - `AnswerTableProjector`

Expected outcome:

- deterministic and LLM answer paths see equivalent normalized table structure

## Phase 3. Make structured table evidence first-class at the prompt boundary

Goal:

Ensure the generic LLM receives structured table evidence in a source-local, table-local, non-fragmented way.

Target area:

- `src/application/prompts/answer_generation/prompt_context/projectors/`
- `src/application/prompts/answer_generation/prompt_context/serializers/`
- `src/application/prompts/answer_generation/answer_prompt_builder.py`

Changes:

- reduce representation splitting between:
  - source payloads
  - tables payload
  - raw appendix prose
- make table-family structure easier to follow in the prompt
- preserve stronger links between:
  - source number
  - table family
  - normalized headers
  - rows
  - axis summary
  - section path

Expected outcome:

- the LLM sees table facts as structured evidence, not mostly prose with optional JSON nearby

## Phase 4. Make deterministic renderers table-first, not extraction-first

Goal:

When hydrated tables exist, renderers should use them as the primary evidence source before depending on partial typed extraction artifacts.

Target area:

- `src/application/services/answer_generation/formatting/renderers/`
- `src/application/services/answer_generation/formatting/`

Changes:

- maintenance answers should recover from normalized tables if `maintenance_entries` are incomplete
- troubleshooting answers should tolerate richer normalized variants, not just perfect three-column cases
- similar treatment should be applied across spare-parts, specification, and certification table answers

Expected outcome:

- deterministic answers become more exact and less dependent on fragile intermediate extraction quality

## Phase 5. Add table-family-aware retrieval pruning before answer generation

Goal:

Reduce answer pollution from lower-value same-intent chunks when a direct hydrated table family exists.

Target area:

- `src/application/workflows/retrieval/`
- `src/infrastructure/retrieval/rerankers/deterministic/`
- `src/application/workflows/question_answering/evidence/`

Changes:

- keep hybrid retrieval intact
- add a narrow post-retrieval, pre-answer evidence preference rule for table-centric intents
- prefer:
  - direct table family anchor
  - direct structured table companions
- demote:
  - overview/context/general same-intent chunks
  - unless they add unique non-table evidence

Expected outcome:

- final answer generation sees cleaner evidence sets for table questions

## Phase 6. Propagate layout-aware metadata farther downstream

Goal:

Use the layout intelligence already computed during parsing in later stages where it can still help.

Target area:

- `src/application/workflows/question_answering/answer_context/`
- `src/application/prompts/answer_generation/prompt_context/`
- possibly vector payload / retrieved metadata if justified

Changes:

- propagate useful layout fields where they can improve:
  - table-family interpretation
  - two-column source disambiguation
  - continuation handling
  - landscape/wide-table handling

Expected outcome:

- fewer downstream mistakes caused by losing page-local layout semantics after parsing

## Phase 7. Add cross-layer regression tests for table-heavy QA

Goal:

Lock in end-to-end quality, not just isolated units.

Target area:

- `tests/unit/application/workflows/question_answering/`
- `tests/unit/application/services/answer_generation/`
- `tests/unit/application/prompts/answer_generation/`
- `tests/unit/application/workflows/retrieval/`

Test themes:

- maintenance interval answers prefer hydrated maintenance matrix evidence
- spare-parts questions do not get diluted by generic maintenance or overview chunks
- troubleshooting questions consume normalized structured rows correctly
- prompt payload preserves structured table facts strongly enough for exact answers
- direct table evidence outranks same-intent narrative noise

Expected outcome:

- future improvements do not regress table-heavy enterprise QA quality

## Phase 8. Treat local Qdrant as dev-only sequential runtime

Goal:

Keep QA debugging stable while quality work continues.

Target area:

- runtime docs
- debug scripts
- CLI notes

Changes:

- explicitly document local-mode sequential usage
- keep live QA probing single-process in local mode
- use server Qdrant when concurrent validation becomes necessary

Expected outcome:

- fewer false signals during debugging

## Recommended Order

1. Phase 1
2. Phase 2
3. Phase 4
4. Phase 5
5. Phase 3
6. Phase 6
7. Phase 7
8. Phase 8

Reason:

- fix data quality first
- then unify structure usage
- then improve deterministic answer extraction
- then reduce retrieval pollution
- then tighten prompt delivery for the generic LLM

## Final Assessment

The current system is not weak because it lacks structure.

It is underperforming because the strongest structure is not yet used consistently across parsing, retrieval, prompt building, and final answer rendering.

The biggest gains now will come from:

- broader parsing-time table normalization
- shared table projection quality across deterministic and LLM paths
- table-family-first evidence selection before answer generation

Those changes would move the system from “good structure, inconsistent exploitation” toward a much stronger enterprise-grade technical-document QA pipeline.
