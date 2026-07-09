# StructuredAnswerContext Enterprise Upgrade Audit And Execution Plan

## Status

- Audit only.
- No implementation changes were made in this pass.
- Repo-wide search was completed for `StructuredAnswerContext` usages, and detailed code inspection was completed for the full answer-context, answer-generation, structured-retrieval, and related test paths.

## 1. Goal

Upgrade the current `StructuredAnswerContext` path into an enterprise-grade answer-context system that:

- preserves useful retrieval and structured-evidence metadata instead of flattening it away
- supports richer answer formatting across maintenance, procedures, specifications, troubleshooting, certifications, identifiers, contacts, tables, and assets
- removes dead or low-value paths
- keeps one file per responsibility
- remains testable, maintainable, and extensible

## 2. Scanned Scope

### Core answer-context files

- `src/application/workflows/question_answering/answer_context/structured_answer_context.py`
- `src/application/workflows/question_answering/answer_context/answer_context_organizer.py`
- `src/application/workflows/question_answering/answer_context/key_value_extractor.py`
- `src/application/workflows/question_answering/answer_context/maintenance_entry_merger.py`
- `src/application/workflows/question_answering/answer_context/source_group_builder.py`
- `src/application/workflows/question_answering/answer_context/section_group_builder.py`
- `src/application/workflows/question_answering/answer_context/structured_fact_key_value_builder.py`

### Upstream workflow / evidence sources

- `src/application/workflows/question_answering/question_answering_workflow.py`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/retrieval/structured/structured_evidence_bundle.py`
- `src/application/workflows/retrieval/structured/structured_evidence_resolver.py`
- `src/application/workflows/retrieval/structured/structured_entity_resolver.py`
- `src/domain/retrieval/retrieved_chunk.py`
- `src/domain/document/entities/chunk.py`

### Downstream generation / formatting

- `src/application/services/answer_generation/answer_generation_service.py`
- `src/application/services/answer_generation/answer_generation_request.py`
- `src/application/services/answer_generation/formatting/answer_format_policy.py`
- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py`
- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py`
- `src/application/prompts/answer_generation/answer_prompt_builder.py`
- `src/application/services/answer_generation/answer_generation_response_schema.py`
- `src/application/services/answer_generation/answer_generation_response_parser.py`

### Tests currently covering this area

- `tests/unit/application/workflows/question_answering/answer_context/*`
- `tests/unit/application/workflows/question_answering/test_question_answering_workflow.py`
- `tests/unit/application/workflows/question_answering/evidence/test_table_evidence_hydrator.py`
- `tests/unit/application/prompts/answer_generation/test_answer_prompt_builder.py`
- `tests/unit/application/services/answer_generation/test_answer_generation_service.py`
- `tests/unit/application/services/answer_generation/formatting/test_answer_format_policy.py`
- `tests/unit/application/services/answer_generation/formatting/test_spare_parts_list_renderer.py`

## 3. Current Flow

### 3.1 Current data path

1. Retrieval returns `RetrievedChunk` objects plus optional structured evidence.
2. `QuestionAnsweringWorkflow` joins approved chunks with structured-evidence source chunks in `_join_structured_facts()`:
   - `src/application/workflows/question_answering/question_answering_workflow.py:438-531`
3. `FinalEvidencePreparer` hydrates table chunks before answer generation.
4. `AnswerContextOrganizer` converts `RetrievedChunk` into `AnswerSource` and derives:
   - source groups
   - section groups
   - key-values
   - maintenance entries
5. `StructuredFactKeyValueBuilder` converts structured identifiers/entities into extra `AnswerKeyValue` rows:
   - `src/application/workflows/question_answering/question_answering_workflow.py:504-530`
6. `AnswerGenerationService` either:
   - uses deterministic renderers for some intents, or
   - builds an LLM prompt using `AnswerPromptBuilder`
7. LLM output is validated only against a one-field JSON schema:
   - `answer_text`

### 3.2 Current strength

The system is already better than a raw chunk dump:

- typed `AnswerSource`
- maintenance-specific typed entries
- deterministic key-value extraction from tables and text
- structured retrieval is joined before generation
- deterministic renderers already exist for identifier and spare-parts answers
- test coverage exists in the right layers

That is a strong base.

## 4. Current Issues

## 4.1 `StructuredAnswerContext` is too thin for the rest of the architecture

`AnswerSource` currently keeps only:

- chunk id
- chunk name
- chunk type
- document id/title
- section path
- page bounds
- score
- content
- one decoded `table_rows` grid

Reference:

- `src/application/workflows/question_answering/answer_context/structured_answer_context.py:11-25`

But upstream `RetrievedChunk` carries more:

- `retrieval_source`
- `section_id`
- `statistics`
- `metadata`
- `identifier_values`

Reference:

- `src/domain/retrieval/retrieved_chunk.py:8-27`

And source `DocumentChunk` carries even more:

- `element_ids`
- `table_ids`
- `picture_ids`
- `chunk_index`
- `chunk_total`
- `embedding_text`

Reference:

- `src/domain/document/entities/chunk.py:7-31`

### Impact

- answer formatting cannot reliably distinguish lexical vs dense vs structured hits
- split-chunk families are not preserved at the answer-context level
- table/picture provenance is partially lost
- context assembly cannot expose chunk family, asset links, or statistics cleanly
- later answer strategies must re-derive data that already existed upstream

## 4.2 Structured semantics are flattened too early

Structured retrieval resolves typed entities plus relationships:

- `StructuredEntityResolver` attaches `related_entities`
- each related entity carries `relationship_type`, `direction`, `status`, `confidence_score`, `entity_type`, `entity_id`, and the related entity payload

References:

- `src/application/workflows/retrieval/structured/structured_entity_resolver.py:93-96`
- `src/application/workflows/retrieval/structured/structured_entity_resolver.py:195-207`

But in the answer path, most of that rich structure is reduced into `AnswerKeyValue` rows:

- `src/application/workflows/question_answering/answer_context/structured_fact_key_value_builder.py:42-104`
- `src/application/workflows/question_answering/question_answering_workflow.py:504-530`

### Impact

- relationships such as manufacturer -> contact point, equipment -> specification, procedure -> warning, or maintenance task -> interval are not preserved as first-class answer context
- the LLM sees labels and values, but not the graph semantics
- deterministic formatters cannot reliably produce enterprise-quality grouped answers from relationships

## 4.3 Structured context is sometimes built and then dropped

If structured entities/identifiers exist but do not produce extra key-values, `_join_structured_facts()` returns `None` for `structured_context`:

- `src/application/workflows/question_answering/question_answering_workflow.py:527-531`

### Impact

- some answer-context work becomes dead-on-arrival
- typed maintenance entries, groups, and diagnostics can be lost even though prepared chunks existed
- this is not just a style issue; it is a behavior gap

## 4.4 `AnswerFormatPolicy.resolve()` is not really resolving anything yet

Current code:

- `src/application/services/answer_generation/formatting/answer_format_policy.py:33-40`

It accepts `structured_context`, then ignores it:

- line 39: `_ = structured_context`

### Impact

- format policy is intent-only, not evidence-aware
- table-rich answers, sparse answers, multi-document answers, contact-heavy answers, and maintenance-summary answers cannot choose the best output policy from real context

This is a confirmed low-value path and a strong dead-code candidate for cleanup/replacement.

## 4.5 Prompt construction still depends on flattened lists instead of typed context views

`AnswerPromptBuilder` currently serializes:

- maintenance entries
- key-values
- source groups
- section groups
- raw source blocks

Reference:

- `src/application/prompts/answer_generation/answer_prompt_builder.py:102-145`

### Impact

- prompt quality depends on ad-hoc textual projections rather than typed, reusable answer views
- prompt builder becomes the place where formatting logic leaks
- future output types will push even more special cases into prompt text

## 4.6 LLM schema is too weak for enterprise answer generation

Current response schema:

- only `answer_text`
- `src/application/services/answer_generation/answer_generation_response_schema.py:8-15`

Current parser:

- `src/application/services/answer_generation/answer_generation_response_parser.py:19-35`

### Impact

- no enforced answer sections
- no enforced limitation note
- no enforced citations structure
- no enforced normalized references or evidence claims
- final answer quality relies too much on prompt wording

## 4.7 Deterministic renderers are useful but fragmented

Current deterministic renderers:

- `IdentifierAnswerRenderer`
- `SparePartsListRenderer`

References:

- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py:141-204`
- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py:52-176`

### Issues

- these renderers bypass the LLM cleanly, which is good
- but they operate on different input abstractions
- they are not backed by a richer, shared typed answer-context model
- output strategies are not unified under a common answer-view contract

## 4.8 Table evidence is partially preserved, not fully modeled

`TableEvidenceHydrator` is good, but still limited:

- only first structured table row grid is stashed in `table_rows_json`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py:72-81`

### Impact

- multi-table chunks are simplified to one row grid
- answer generation does not get a first-class table evidence model
- deterministic table answers still need their own parsing rules

## 4.9 Source grouping is prompt-facing, not answer-facing

`AnswerSourceGroup` and `AnswerSectionGroup` currently exist, but their main downstream consumer is the prompt builder:

- `src/application/workflows/question_answering/answer_context/structured_answer_context.py:27-40`
- `src/application/prompts/answer_generation/answer_prompt_builder.py:125-144`

### Impact

- groups help the prompt, but they are not yet reusable by deterministic renderers, CLI presentation, or research-style structured synthesis
- they are not dead, but they are under-leveraged

## 4.10 Current tests lock in only the current limited model

Examples:

- organizer tests validate source count, grouping, key-values, maintenance entries
- policy tests validate stability, not context-aware behavior

References:

- `tests/unit/application/workflows/question_answering/answer_context/test_answer_context_organizer.py:29-172`
- `tests/unit/application/services/answer_generation/formatting/test_answer_format_policy.py:30-65`

### Impact

- current tests are good for regression control
- they do not yet protect a richer enterprise answer-context model

## 5. Dead Code / Low-Value Path Review

## 5.1 Confirmed low-value or dead-path behavior

### A. `AnswerFormatPolicy.resolve(..., structured_context=...)`

- Parameter is accepted but ignored.
- This should either become a real resolver or be removed/replaced.

Reference:

- `src/application/services/answer_generation/formatting/answer_format_policy.py:33-40`

### B. Structured context creation can be discarded when no extra key-values are produced

- This is a dead-path behavior, not a dead file.

Reference:

- `src/application/workflows/question_answering/question_answering_workflow.py:527-531`

### C. Prompt-only grouping models

- `AnswerSourceGroup` and `AnswerSectionGroup` are not dead, but currently underused and likely need redesign or stronger consumers.

## 5.2 Removal candidates after replacement exists

These should not be deleted immediately. They should be removed only after the new typed answer-context path is in place:

- prompt-only string grouping blocks if replaced by typed answer views
- ad-hoc field-label flattening that becomes redundant once typed answer sections exist
- duplicated spare-parts / identifier formatting branches if moved behind a unified rendering policy layer

## 6. Enterprise Target State

## 6.1 What `StructuredAnswerContext` should become

It should become the canonical answer-evidence projection for question answering.

That means:

- not just a prompt helper
- not just a maintenance formatter helper
- not just a container for flattened key-values

It should carry:

- normalized answer sources
- typed structured evidence views
- typed relationships
- answer-ready groups and summaries
- enough metadata for deterministic renderers and LLM prompts to share the same truth

## 6.2 Recommended target responsibilities

### Keep in `StructuredAnswerContext`

- canonical source list
- canonical answer intent
- evidence diagnostics
- typed answer-facing evidence projections

### Move out of `AnswerPromptBuilder`

- answer-shape decisions
- context-aware formatting choices
- special-case structured summarization logic

### Keep `AnswerPromptBuilder` focused on

- serializing already-prepared answer context into prompt text
- adding grounding rules and schema rules
- not inventing business interpretation

## 7. Proposed Package Direction

Keep the existing package root:

- `src/application/workflows/question_answering/answer_context/`

Refactor internally into grouped subfolders while preserving stable exports through `__init__.py`.

### Proposed internal structure

```text
src/application/workflows/question_answering/answer_context/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── answer_source.py
│   ├── answer_groups.py
│   ├── structured_answer_context.py
│   ├── answer_key_value.py
│   ├── answer_maintenance_entry.py
│   ├── answer_table_evidence.py
│   ├── answer_asset_evidence.py
│   ├── answer_structured_entity.py
│   └── answer_relationship.py
├── builders/
│   ├── __init__.py
│   ├── answer_context_organizer.py
│   ├── source_group_builder.py
│   ├── section_group_builder.py
│   ├── structured_source_builder.py
│   └── structured_evidence_view_builder.py
├── extractors/
│   ├── __init__.py
│   ├── key_value_extractor.py
│   ├── maintenance_entry_extractor.py
│   └── table_evidence_extractor.py
├── mergers/
│   ├── __init__.py
│   └── maintenance_entry_merger.py
└── adapters/
    ├── __init__.py
    └── structured_fact_key_value_builder.py
```

This keeps one file per responsibility and avoids turning `StructuredAnswerContext` into a dump file.

## 8. Files Likely To Change In Implementation

## 8.1 Must-change files

- `src/application/workflows/question_answering/answer_context/structured_answer_context.py`
- `src/application/workflows/question_answering/answer_context/answer_context_organizer.py`
- `src/application/workflows/question_answering/answer_context/key_value_extractor.py`
- `src/application/workflows/question_answering/answer_context/maintenance_entry_merger.py`
- `src/application/workflows/question_answering/answer_context/source_group_builder.py`
- `src/application/workflows/question_answering/answer_context/section_group_builder.py`
- `src/application/workflows/question_answering/answer_context/structured_fact_key_value_builder.py`
- `src/application/workflows/question_answering/question_answering_workflow.py`
- `src/application/services/answer_generation/formatting/answer_format_policy.py`
- `src/application/prompts/answer_generation/answer_prompt_builder.py`
- `src/application/services/answer_generation/answer_generation_service.py`
- `src/application/services/answer_generation/answer_generation_response_schema.py`
- `src/application/services/answer_generation/answer_generation_response_parser.py`

## 8.2 Likely supporting changes

- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/retrieval/structured/structured_evidence_bundle.py`
- `src/application/workflows/retrieval/structured/structured_evidence_resolver.py`
- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py`
- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py`

## 8.3 Test files that will need updates

- `tests/unit/application/workflows/question_answering/answer_context/*`
- `tests/unit/application/workflows/question_answering/test_question_answering_workflow.py`
- `tests/unit/application/prompts/answer_generation/test_answer_prompt_builder.py`
- `tests/unit/application/services/answer_generation/test_answer_generation_service.py`
- `tests/unit/application/services/answer_generation/formatting/test_answer_format_policy.py`
- `tests/unit/application/services/answer_generation/formatting/test_spare_parts_list_renderer.py`

## 9. Proposed Solution Set

## 9.1 Expand the answer source model instead of re-deriving metadata later

Add answer-facing fields for:

- `retrieval_source`
- `section_id`
- `statistics`
- `identifier_values`
- `metadata`
- `table_ids`
- `picture_ids`
- `chunk_index`
- `chunk_total`
- `family_key` or equivalent split-family reference

This should be a direct, clean answer-facing projection, not a copy of the whole chunk model.

## 9.2 Introduce first-class structured evidence views

Instead of flattening everything into `AnswerKeyValue`, add typed answer-context collections such as:

- `specification_entries`
- `procedure_entries`
- `troubleshooting_entries`
- `safety_entries`
- `contact_entries`
- `equipment_entries`
- `certification_entries`
- `table_evidence`
- `asset_evidence`
- `relationship_views`

Maintenance already has a strong typed path. The rest should reach the same level.

## 9.3 Preserve structured relationships

Add answer-context types that preserve:

- source entity type
- target entity type
- relationship type
- confidence
- direction
- source chunk references

This will let the answer layer generate cleaner manufacturer/contact, equipment/specification, and procedure/warning answers.

## 9.4 Make format-policy resolution real

`AnswerFormatPolicy.resolve()` should use:

- answer intent
- evidence density
- presence of tables
- presence of typed entries
- presence of structured relationships
- whether evidence is single-document vs mixed

This turns policy from static lookup into real answer orchestration.

## 9.5 Unify deterministic rendering on top of the same typed context

Do not remove deterministic renderers.

Instead:

- keep deterministic rendering for high-confidence, structured answer types
- make them consume the same enriched `StructuredAnswerContext`
- avoid custom parsing branches where the answer context already knows the facts

## 9.6 Strengthen the answer-generation schema

The LLM response schema should evolve from:

- `answer_text`

to something closer to:

- `answer_text`
- `limitation_note`
- `sections`
- `reference_notes`

This does not mean exposing raw internal ids. It means enforcing answer structure instead of leaving everything to prose.

## 9.7 Stop dropping structured context

`QuestionAnsweringWorkflow._join_structured_facts()` should keep the structured context whenever it was successfully built, not only when extra key-values exist.

That is a correctness upgrade, not just a cleanup.

## 10. Execution Plan For Review

## Phase 1 - Baseline protection

- add an audit snapshot test plan for current behavior
- add coverage around current `StructuredAnswerContext` construction
- add regression tests around structured-entity joining and structured-context retention

## Phase 2 - Model refactor

- split `structured_answer_context.py` into smaller answer-context model files
- keep `src.` imports and stable re-exports
- do not change behavior yet beyond file moves

## Phase 3 - Source enrichment

- enrich `AnswerSource` projection with missing retrieval/chunk metadata
- update organizer tests
- ensure no consumer breaks

## Phase 4 - Typed structured-evidence views

- add first-class answer models for structured entities, relationships, tables, and assets
- keep `AnswerKeyValue` as a convenience projection, not the only structured view

## Phase 5 - Organizer redesign

- keep `AnswerContextOrganizer` as orchestration only
- move extraction logic into focused builders/extractors
- ensure maintenance extraction remains intact

## Phase 6 - Format-policy upgrade

- make `AnswerFormatPolicy.resolve()` context-aware
- remove the current fake resolve path
- add intent-plus-context policy tests

## Phase 7 - Renderer unification

- refactor deterministic renderers to consume richer typed context
- remove duplicate ad-hoc parsing where context already provides the same information

## Phase 8 - Prompt/schema hardening

- upgrade prompt builder to serialize the richer context cleanly
- strengthen the pydantic response schema for answer generation
- keep parser strict

## Phase 9 - Cleanup / dead code removal

- remove replaced prompt-only helpers
- remove obsolete flattening logic
- remove no-longer-used projections
- update `__init__.py` exports

## Phase 10 - Full validation

- targeted unit tests first
- then question-answering, prompt, and langgraph integration tests touching this path

## 11. Test Plan For Implementation

### New tests to add

- `AnswerSource` preserves retrieval metadata, split-family metadata, and asset/table metadata
- structured relationships survive into `StructuredAnswerContext`
- context is retained even when no extra key-values are produced
- `AnswerFormatPolicy.resolve()` changes behavior based on real context
- deterministic renderers consume typed context instead of reparsing raw text where possible
- prompt builder emits richer organized context without leaking internal ids
- answer-generation schema rejects malformed structured output cleanly

### Existing tests to update

- organizer tests
- format policy tests
- answer generation service tests
- prompt builder tests
- workflow tests that assert current structured-context behavior

## 12. Recommended Review Decisions Before Implementation

Please review and decide these before the code pass:

1. Should `StructuredAnswerContext` remain the single canonical answer-context DTO for both deterministic renderers and LLM prompting?
   - Recommended: yes.

2. Should we keep `AnswerKeyValue` as a secondary convenience view rather than the main structured-evidence view?
   - Recommended: yes.

3. Should deterministic answer rendering expand beyond identifiers and spare parts once typed structured views exist?
   - Recommended: yes, but phase it after the context refactor.

4. Should prompt/output schema strengthening happen in the same implementation wave or after context refactor stabilization?
   - Recommended: same wave, after context refactor and before cleanup.

## 13. Final Recommendation

The right upgrade path is not to patch the prompt builder again.

The right path is:

- enrich the answer-context model
- preserve structured semantics
- make format policy context-aware
- unify deterministic and LLM answer generation on the same typed context
- then remove the dead and low-value code that becomes unnecessary

That will move this area from "helpful prompt helper" to "enterprise answer-evidence layer".
