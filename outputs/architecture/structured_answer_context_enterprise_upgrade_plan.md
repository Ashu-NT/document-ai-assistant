# StructuredAnswerContext Enterprise Upgrade Audit And Execution Plan

## Status

- Audit only.
- No implementation changes were made in this pass.
- Repo-wide search was completed for `StructuredAnswerContext` usages, and detailed code inspection was completed for the full answer-context, answer-generation, structured-retrieval, and related test paths.

## 0. Post-Audit Amendment

Two fixes landed in this codebase after this audit was written (same day, different session, merged via `git merge`). Neither is a false alarm against anything below, but both change file/line references in a handful of the "Must-change" files and neither was caught by this audit's scanned scope, so they're recorded here rather than silently absorbed into the line numbers below.

1. **A second, redundant `AnswerIntentAnalyzer.analyze()` call per QA turn was eliminated.** `QuestionAnsweringWorkflow` and `AnswerGenerationService` each held their own independently-constructed `AnswerIntentAnalyzer` instance, and both called `analyze()` with equivalent inputs whenever structured facts were resolved — one to build `structured_context`, one inside `AnswerGenerationService._resolve_request()`. Not just wasted work: nothing enforced the two computations saw identical chunk sets, so a future caller of `AnswerGenerationRequest.max_context_chunks` (see 4.11 below — still unused) could have made them disagree, leaving `structured_context`'s already-extracted data shaped for an intent the format policy no longer agreed with. Fixed by adding `AnswerGenerationRequest.answer_intent_decision: AnswerIntentDecision | None`, threading the workflow's already-computed decision through it, and having `AnswerGenerationService._resolve_intent_decision()` reuse it instead of recomputing. This is **not** the same issue as 4.3/9.7 below (structured_context being dropped) — that issue is still open.
2. **A 4th independently-drifted copy of the identifier-marker taxonomy was deduplicated.** `IdentifierAnswerRenderer._QUESTION_TYPE_MARKERS` was a near-verbatim, silently-drifted copy of `StructuredIdentifierQueryAnalyzer._IDENTIFIER_INVENTORY_MARKERS` (missing "part no"/"serial no" short-form aliases the renderer's copy had — so a question like "what's the part no?" was identifier-scoped by the final renderer but not by the earlier structured-evidence resolver). Both now import a shared `IDENTIFIER_TYPE_MARKERS` dict from `src/application/workflows/shared/identifier_type_markers.py` (new file). This file was outside this audit's "Scanned Scope" (section 2) entirely — see 2.1 below.

References for both fixes: `src/application/services/answer_generation/answer_generation_request.py`, `src/application/services/answer_generation/answer_generation_service.py` (`_resolve_intent_decision`), `src/application/workflows/question_answering/question_answering_workflow.py` (`_resolve_structured_answer_intent_decision`), `src/application/workflows/shared/identifier_type_markers.py`, `src/application/services/answer_generation/formatting/identifier_answer_renderer.py`, `src/application/workflows/retrieval/structured/structured_identifier_query_analyzer.py`.

All line references elsewhere in this document have been re-verified against the current codebase and corrected where these two fixes shifted them (`question_answering_workflow.py`, `identifier_answer_renderer.py`). Every other reference in this document (structured_answer_context.py, retrieved_chunk.py, chunk.py, structured_entity_resolver.py, structured_fact_key_value_builder.py, answer_format_policy.py, answer_prompt_builder.py, answer_generation_response_schema.py, answer_generation_response_parser.py, spare_parts_list_renderer.py, table_evidence_hydrator.py, and the cited test files) was re-checked and is still accurate — those files were untouched by the two fixes above.

## 0.1 Reviewer Follow-Up On The Amendment

The amendment is directionally correct and improves the original audit in meaningful ways.

### Confirmed strong additions

1. The duplicate `AnswerIntentAnalyzer.analyze()` finding was real, the fix landed cleanly, and the new request seam is now explicit:
   - `src/application/services/answer_generation/answer_generation_request.py:27-39`
   - `src/application/services/answer_generation/answer_generation_service.py:174-235`
   - `src/application/workflows/question_answering/question_answering_workflow.py:360-380`, `:437-535`
2. The shared identifier-marker extraction is a real architectural improvement, not just cleanup:
   - `src/application/workflows/shared/identifier_type_markers.py`
   - `src/application/workflows/retrieval/structured/structured_identifier_query_analyzer.py:3-46`
   - `src/application/services/answer_generation/formatting/identifier_answer_renderer.py:13-157`
   - tests exist:
     - `tests/unit/application/workflows/shared/test_identifier_type_markers.py`
3. Expanding scope to include the structured query-analysis layer was the right correction. That layer decides what structured evidence can ever reach `StructuredAnswerContext`, so it belongs in this upgrade.

### Reviewer adjustments to the plan

1. `AnswerGenerationRequest.max_context_chunks` should not remain a passive field during this refactor. It now has less risk than before because `answer_intent_decision` can be threaded through, but it is still an unresolved behavior seam if any future caller passes:
   - `structured_context` built on one chunk set
   - `max_context_chunks` that truncates a different chunk set
   - no explicit plan for whether truncation happens before or after context organization

   This should become an explicit Phase 1 design decision:
   - either remove it now
   - or define one canonical truncation point upstream of both `AnswerContextOrganizer` and `AnswerGenerationService`

2. `AnswerMaintenanceEntry`'s duplicated reference modeling should be collapsed during the model-refactor phase, not deferred. If the answer-context models are being split anyway, keeping both `references` and parallel flat reference fields through that rewrite would carry forward avoidable sync risk:
   - `src/application/workflows/question_answering/answer_context/structured_answer_context.py:52-74`
   - `src/application/prompts/answer_generation/maintenance_prompt_context_formatter.py:52-109`

3. The new observability/versioning point is good and should move earlier in the execution order. Adding diagnostics and rules-version markers after the large refactor would make it harder to measure the refactor itself. It is better treated as an early hardening layer around the current extractors/parsers before or alongside the format-policy rewrite.

4. The write-only confidence fields should not automatically be promoted into the new enterprise model. Unless a calibrated consumer is designed, the safer default is removal during cleanup rather than wider propagation.

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

### 2.1 Gap in original scope (added in this amendment)

The original scan stopped at the resolver/bundle/entity-resolver layer and did not cover the layer that decides *what* structured evidence gets resolved in the first place. That layer directly shapes what `StructuredAnswerContext` ever sees, so it belongs in scope for any enterprise upgrade of this path:

- `src/application/workflows/retrieval/structured/structured_evidence_query_analyzer.py` — keyword-driven `entity_types`/`identifier_types` selection that feeds `StructuredEvidenceResolver.resolve()`
- `src/application/workflows/retrieval/structured/structured_identifier_query_analyzer.py` — inventory-query detection and requested-identifier-type extraction
- `src/application/workflows/retrieval/structured/structured_evidence_query_analysis.py` — the DTO both above produce
- `src/application/workflows/shared/identifier_type_markers.py` (new) — the shared marker dict introduced by the fix in section 0.2

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
   - `src/application/workflows/question_answering/question_answering_workflow.py:437-535` (line numbers corrected in this amendment — see section 0)
3. `FinalEvidencePreparer` hydrates table chunks before answer generation.
4. `AnswerContextOrganizer` converts `RetrievedChunk` into `AnswerSource` and derives:
   - source groups
   - section groups
   - key-values
   - maintenance entries
5. `StructuredFactKeyValueBuilder` converts structured identifiers/entities into extra `AnswerKeyValue` rows:
   - `src/application/workflows/question_answering/question_answering_workflow.py:508-529` (line numbers corrected in this amendment — see section 0)
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
- `src/application/workflows/question_answering/question_answering_workflow.py:508-529` (line numbers corrected in this amendment — see section 0)

### Impact

- relationships such as manufacturer -> contact point, equipment -> specification, procedure -> warning, or maintenance task -> interval are not preserved as first-class answer context
- the LLM sees labels and values, but not the graph semantics
- deterministic formatters cannot reliably produce enterprise-quality grouped answers from relationships

## 4.3 Structured context is sometimes built and then dropped

If structured entities/identifiers exist but do not produce extra key-values, `_join_structured_facts()` returns `None` for `structured_context`:

- `src/application/workflows/question_answering/question_answering_workflow.py:531-532` (line numbers corrected in this amendment — see section 0)

### Impact

- some answer-context work becomes dead-on-arrival
- typed maintenance entries, groups, and diagnostics can be lost even though prepared chunks existed
- this is not just a style issue; it is a behavior gap

Still open as of this amendment. Note that `_join_structured_facts()` now also computes an `AnswerIntentDecision` on this path (see section 0.1) — that specific piece of work is no longer wasted (it is threaded through to `AnswerGenerationRequest.answer_intent_decision` either way), but `structured_context` itself — the organized sources, groups, key-values, and maintenance entries — is still thrown away on this branch exactly as described above. The intent-recompute fix and this dead-context-drop issue are separate problems; only the former is fixed.

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

- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py:64-157` (line numbers corrected in this amendment — a ~74-line duplicated marker dict was removed from above the class as part of the fix in section 0.2, shifting everything below it)
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

## 4.11 Two write-only "confidence" fields (missed in original audit)

`AnswerKeyValue.confidence` and `AnswerMaintenanceEntry.confidence` are populated with hardcoded values (`0.9`, `0.88`, or `max(left, right) or None` on merge) but nothing in `src/` ever reads them back — not the prompt builder, not a guardrail, not diagnostics.

References:

- `src/application/workflows/question_answering/answer_context/structured_answer_context.py:44-49` (`AnswerKeyValue.confidence`), `:53-67` (`AnswerMaintenanceEntry.confidence`)
- `src/application/workflows/question_answering/answer_context/key_value_extractor.py:166`, `:219` (hardcoded assignment)
- `src/application/workflows/question_answering/answer_context/maintenance_entry_merger.py:138` (`max(left.confidence or 0.0, right.confidence or 0.0) or None`)

### Impact

- a fabricated, uncalibrated number is computed and carried on every `AnswerKeyValue`/`AnswerMaintenanceEntry` for no consumer
- if a real confidence-weighted answer strategy is added later (section 9.2/9.3), whoever wires it up needs to first decide whether these existing numbers mean anything or need to be recalibrated from scratch — right now they are decorative

## 4.12 A dead configuration knob with a live divergence risk if ever wired up

`AnswerGenerationRequest.max_context_chunks` is declared and checked, but no production caller ever sets it.

References:

- `src/application/services/answer_generation/answer_generation_request.py` (field declaration)
- `src/application/services/answer_generation/answer_generation_service.py` (`_resolve_request`: `if request.max_context_chunks is not None: context_chunks = context_chunks[: request.max_context_chunks]`)

### Impact

- this is the exact seam that made the pre-amendment double-intent-computation bug (section 0.1) a live risk rather than a theoretical one: if a future caller sets `max_context_chunks` to cap prompt size, the truncated `context_chunks` would only affect `AnswerGenerationService`'s own fallback `analyze()` path (when no `answer_intent_decision` was passed) — a caller that both sets `max_context_chunks` *and* relies on the fallback recompute could still get a different intent than whatever built `structured_context` upstream
- whoever wires this up next should be aware of that interaction, not just the truncation itself

## 4.13 Redundant parallel data modeling in `AnswerMaintenanceEntry`

`AnswerMaintenanceEntry` carries both a `references: list[AnswerMaintenanceReference]` (each with its own `source_number`/`page_start`/`page_end`/`section_path`) *and* flat parallel lists (`source_numbers`, `section_paths`) plus scalar fields (`page_start`, `page_end`) covering the same four facts.

References:

- `src/application/workflows/question_answering/answer_context/structured_answer_context.py:52-74`
- `src/application/prompts/answer_generation/maintenance_prompt_context_formatter.py:52-77` (`_reference_lines` reads `entry.references`, falling back to constructing one from the flat fields; `_page_lines`/`_section_lines` separately read `entry.source_numbers`/`entry.section_paths`, falling back to deriving them from `references`)
- `src/application/workflows/question_answering/answer_context/maintenance_entry_merger.py` (`_merge_pair`/`_normalized_copy` manually keep both representations in sync on every merge)

### Impact

- two representations of the same underlying facts must be kept in sync by hand; nothing enforces `len(references) == len(source_numbers) == len(section_paths)`
- a future edit to one representation without the other would silently desync page/section references in the rendered maintenance answer
- section 9.2's "typed structured evidence views" work is a natural place to collapse this to one representation instead of adding a fifth alongside it

## 4.14 No versioning or observability parity on the formatting layer

`AnswerIntentAnalyzer` and `RetrievalQueryIntentInferer` both carry a `*_RULES_VERSION` constant plus structured `_logger.info(...)` lines on every resolution/fallback, so a future answer-quality regression can be correlated against a specific rule-pack version. The pieces that decide what the user actually *sees* have none of this:

- `AnswerFormatPolicy` (static `_POLICIES` lookup)
- `KeyValueExtractor` / `MaintenanceEntryMerger` (regex/heuristic extraction and fuzzy merge)
- `src/application/services/answer_generation/formatting/spare_parts_table_parser.py` (4 distinct table-layout strategies)

`SparePartsTableParser` already tracks `dropped_row_count`/`partial` internally, but that signal only ever reaches the user as a single "Only partial row content was available in the retrieved context." sentence in the rendered answer — it is not surfaced as a queryable diagnostic the way `RetrievalWorkflowResult.diagnostics`/`GeneratedAnswer.diagnostics` surface everything else in this pipeline.

### Impact

- if a new vendor manual's table layout silently drops rows at scale, or a `KeyValueExtractor`/`MaintenanceEntryMerger` rule change regresses extraction quality, there is currently no version marker and no diagnostic count to detect it with — only the final rendered text

## 4.15 No exhaustiveness guard across the `AnswerIntent` enum

Three independent lookup tables must all stay in sync with `AnswerIntent`'s members, and nothing enforces that:

- `AnswerFormatPolicy._POLICIES` (`src/application/services/answer_generation/formatting/answer_format_policy.py`)
- `AnswerIntentAnalyzer._CHUNK_TYPE_TO_INTENT` (`src/application/services/answer_generation/intent/answer_intent_analyzer.py`)
- `AnswerIntentAnalyzer._RETRIEVAL_INTENT_TO_ANSWER_INTENT` (same file)

### Impact

- this is the exact shape of bug that was found and fixed elsewhere in this codebase on a sibling enum (`RetrievalQueryIntent`/`AnswerIntent` cross-taxonomy confusion produced a dead `elif intent == "certification":` branch in `StructuredEvidenceQueryAnalyzer.analyze()`, fixed in an earlier session)
- a new `AnswerIntent` member added later could silently fall through to `GENERAL` formatting in one of these three maps and not the others, with no test catching the gap — a parametrized test iterating `AnswerIntent` against all three maps would close this cheaply and should be added alongside any section 9 work that touches these maps

## 5. Dead Code / Low-Value Path Review

## 5.1 Confirmed low-value or dead-path behavior

### A. `AnswerFormatPolicy.resolve(..., structured_context=...)`

- Parameter is accepted but ignored.
- This should either become a real resolver or be removed/replaced.

Reference:

- `src/application/services/answer_generation/formatting/answer_format_policy.py:33-40`

### B. Structured context creation can be discarded when no extra key-values are produced

- This is a dead-path behavior, not a dead file.
- Still open as of this amendment (see 4.3).

Reference:

- `src/application/workflows/question_answering/question_answering_workflow.py:531-532` (line numbers corrected in this amendment — see section 0)

### C. Prompt-only grouping models

- `AnswerSourceGroup` and `AnswerSectionGroup` are not dead, but currently underused and likely need redesign or stronger consumers.

### D. `AnswerKeyValue.confidence` / `AnswerMaintenanceEntry.confidence` (missed in original audit)

- Written on every construction, never read anywhere in `src/`.
- See section 4.11.

Reference:

- `src/application/workflows/question_answering/answer_context/structured_answer_context.py:49`, `:66`

### E. `AnswerGenerationRequest.max_context_chunks` (missed in original audit)

- Declared and checked, never set by the one production caller (`QuestionAnsweringWorkflow`).
- See section 4.12 for why this is not just inert — it is the seam that made the pre-amendment double-intent-computation bug reachable.

Reference:

- `src/application/services/answer_generation/answer_generation_request.py`

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
|-- __init__.py
|-- models/
|   |-- __init__.py
|   |-- answer_source.py
|   |-- answer_groups.py
|   |-- structured_answer_context.py
|   |-- answer_key_value.py
|   |-- answer_maintenance_entry.py
|   |-- answer_table_evidence.py
|   |-- answer_asset_evidence.py
|   |-- answer_structured_entity.py
|   `-- answer_relationship.py
|-- builders/
|   |-- __init__.py
|   |-- answer_context_organizer.py
|   |-- source_group_builder.py
|   |-- section_group_builder.py
|   |-- structured_source_builder.py
|   `-- structured_evidence_view_builder.py
|-- extractors/
|   |-- __init__.py
|   |-- key_value_extractor.py
|   |-- maintenance_entry_extractor.py
|   `-- table_evidence_extractor.py
|-- mergers/
|   |-- __init__.py
|   `-- maintenance_entry_merger.py
`-- adapters/
    |-- __init__.py
    `-- structured_fact_key_value_builder.py
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
- `src/application/services/answer_generation/answer_generation_request.py` (added in this amendment — missing from the original list despite being the DTO section 9's typed-context work would need to expand; already carries one new field, `answer_intent_decision`, from the fix in section 0.1)
- `src/application/services/answer_generation/answer_generation_response_schema.py`
- `src/application/services/answer_generation/answer_generation_response_parser.py`

## 8.2 Likely supporting changes

- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/retrieval/structured/structured_evidence_bundle.py`
- `src/application/workflows/retrieval/structured/structured_evidence_resolver.py`
- `src/application/workflows/retrieval/structured/structured_evidence_query_analyzer.py` (added in this amendment — see 2.1)
- `src/application/workflows/retrieval/structured/structured_identifier_query_analyzer.py` (added in this amendment — see 2.1)
- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py`
- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py`
- `src/application/services/answer_generation/formatting/spare_parts_table_parser.py` (added in this amendment — see 4.14)
- `src/application/services/answer_generation/intent/answer_intent_analyzer.py` (added in this amendment — see 4.15)

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

## 9.8 Close the enum-exhaustiveness gap (added in this amendment)

Add a parametrized test iterating every `AnswerIntent` member and asserting it has an entry in `AnswerFormatPolicy._POLICIES`, and treat `_CHUNK_TYPE_TO_INTENT`/`_RETRIEVAL_INTENT_TO_ANSWER_INTENT` as intentionally partial mappings (not every intent needs a chunk-type or retrieval-intent trigger) — but document that distinction explicitly rather than leaving it implicit. See 4.15.

## 9.9 Retire or recalibrate the decorative confidence fields (added in this amendment)

Before section 9.2/9.3 add new typed evidence views, decide whether `AnswerKeyValue.confidence`/`AnswerMaintenanceEntry.confidence` are worth keeping. Either wire them into something that reads them (a low-confidence-evidence warning in the format policy, for instance — which would also give 9.4's context-aware policy work a concrete first signal to consume) or remove them rather than propagating an uncalibrated number into whatever the new typed views become. See 4.11.

## 9.10 Add rules-version constants and diagnostic counts to the formatting layer (added in this amendment)

Mirror the `*_RULES_VERSION` + structured-logging pattern already used by `AnswerIntentAnalyzer`/`RetrievalQueryIntentInferer` on `AnswerFormatPolicy`, `KeyValueExtractor`, and `MaintenanceEntryMerger`. Surface `SparePartsTableParser`'s existing `dropped_row_count`/`partial` tracking as a queryable diagnostic (matching how every other stage in this pipeline reports through a `diagnostics` dict) instead of only a one-line notice in the rendered answer text. See 4.14.

## 10. Execution Plan For Review

### 10.0 Traceability Matrix

Every issue in sections 4 and 5, and every solution in section 9 (including the reviewer's four adjustments in section 0.1), maps to exactly one phase below. Nothing found in this audit is left without an assigned remediation phase.

| Issue | Phase(s) | Solution ref |
|---|---|---|
| 4.1 `AnswerSource` too thin | Phase 3 | 9.1 |
| 4.2 structured semantics flattened too early | Phase 4 | 9.2, 9.3 |
| 4.3 / 5.1.B structured context sometimes dropped | Phase 4 | 9.7 |
| 4.4 / 5.1.A `AnswerFormatPolicy.resolve()` ignores context | Phase 6 | 9.4 |
| 4.5 prompt depends on flattened lists | Phase 8 | 9.6 |
| 4.6 LLM schema too weak | Phase 8 | 9.6 |
| 4.7 deterministic renderers fragmented | Phase 7 | 9.5 |
| 4.8 table evidence partially modeled | Phase 4 | 9.2 (`table_evidence`) |
| 4.9 groups are prompt-facing only | Phase 5, Phase 7 | 9.5 |
| 4.10 tests lock in the limited model | Phase 1, Phase 10 | section 11 |
| 4.11 / 5.1.D dead `confidence` fields | Phase 9 | 9.9, reviewer 0.1 #4 |
| 4.12 / 5.1.E dead `max_context_chunks` | Phase 1 (decision), Phase 3 (enforcement) | reviewer 0.1 #1 |
| 4.13 redundant maintenance-entry data model | Phase 2 | reviewer 0.1 #2 |
| 4.14 no rules-version / observability parity | Phase 6 | 9.10, reviewer 0.1 #3 |
| 4.15 no `AnswerIntent` exhaustiveness guard | Phase 1 | 9.8 |

## Phase 1 - Baseline protection

- add an audit snapshot test plan for current behavior
- add coverage around current `StructuredAnswerContext` construction
- add regression tests around structured-entity joining and structured-context retention
- add/keep regression coverage for pre-resolved `answer_intent_decision` reuse
- add the `AnswerIntent` exhaustiveness guard tests called out in 9.8
- make an explicit keep/remove/design decision for `AnswerGenerationRequest.max_context_chunks` before the refactor starts

## Phase 2 - Model refactor

- split `structured_answer_context.py` into smaller answer-context model files
- keep `src.` imports and stable re-exports
- collapse `AnswerMaintenanceEntry`'s duplicated reference representations while models are being split
- do not change answer behavior yet beyond structural cleanup and removal of duplicated internal representations
- **must be executed as behavior-preserving:** the reference-representation collapse touches three consumers (`MaintenanceEntryMerger`, `MaintenancePromptContextFormatter`, `AnswerContextOrganizer`) — update all three in this same phase, not a subset, and keep rendered maintenance-answer output byte-for-byte identical at this stage (verify via `tests/unit/application/workflows/question_answering/answer_context/test_maintenance_entry_merger.py` and the maintenance-path assertions in `test_answer_generation_service.py`, both green with no assertion changes). Any answer-shape improvement that collapsing enables is deferred to Phase 4+, not bundled in here.

## Phase 3 - Source enrichment

- enrich `AnswerSource` projection with missing retrieval/chunk metadata
- if `max_context_chunks` is kept, enforce its canonical truncation point here so organizer/builders/renderers all see the same chunk slice
- update organizer tests
- ensure no consumer breaks

## Phase 4 - Typed structured-evidence views

- **First change in this phase, ahead of the typed-view work below:** make `QuestionAnsweringWorkflow._join_structured_facts()` retain the built `structured_context` whenever it was successfully organized, not only when extra `AnswerKeyValue` rows were produced (closes 4.3/9.7). This is the clearest live production correctness bug in this path — `structured_context` is fully organized and then discarded — so it lands first and is not gated on the rest of Phase 4. If the team wants risk reduction sooner than Phase 4's start, this single change can be pulled forward and shipped as its own micro-fix ahead of Phase 2/3 without waiting on the model refactor; it needs no new types, only removing the dead-path check.
- add first-class answer models for structured entities, relationships, tables, and assets
- keep `AnswerKeyValue` as a convenience projection, not the only structured view

## Phase 5 - Organizer redesign

- keep `AnswerContextOrganizer` as orchestration only
- move extraction logic into focused builders/extractors
- ensure maintenance extraction remains intact

## Phase 6 - Observability and Format-Policy Upgrade

- add rules-version constants and diagnostics parity for:
  - `AnswerFormatPolicy`
  - `KeyValueExtractor`
  - `MaintenanceEntryMerger`
  - `SparePartsTableParser`
- surface table-parser partial/drop counts as structured diagnostics, not only rendered prose
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
- remove write-only confidence fields unless a calibrated consumer has been deliberately introduced
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
- every `AnswerIntent` member has a corresponding `AnswerFormatPolicy._POLICIES` entry (added in this amendment — see 9.8)
- `AnswerGenerationService` does not recompute `AnswerIntentAnalyzer.analyze()` when `AnswerGenerationRequest.answer_intent_decision` is already set, and still computes it when absent (added in this amendment — regression coverage for section 0.1 already exists in `tests/unit/application/services/answer_generation/test_answer_generation_service.py` and `tests/unit/application/workflows/question_answering/test_question_answering_workflow.py::test_answer_intent_is_resolved_exactly_once_when_structured_facts_are_joined`; keep these passing through the refactor)

### Existing tests to update

- organizer tests
- format policy tests
- answer generation service tests
- prompt builder tests
- workflow tests that assert current structured-context behavior

## 12. Decisions

These were open review questions in the original audit. None were contested, so each is adopted here using this document's own stated recommendation, and the numbered phases above are written against these answers. Revisit before starting the phase noted if the team's priorities change.

1. Should `StructuredAnswerContext` remain the single canonical answer-context DTO for both deterministic renderers and LLM prompting?
   - **Decision: Yes.** Phases 4, 5, and 7 are written on this basis — renderer unification (Phase 7) only makes sense if there is one shared DTO to unify on.

2. Should we keep `AnswerKeyValue` as a secondary convenience view rather than the main structured-evidence view?
   - **Decision: Yes.** Phase 4 explicitly keeps it as a convenience projection alongside the new typed views, not a replacement for them.

3. Should deterministic answer rendering expand beyond identifiers and spare parts once typed structured views exist?
   - **Decision: Yes, phased after the context refactor.** This is why Phase 7 (renderer unification) is sequenced after Phase 4 (typed views), not before.

4. Should prompt/output schema strengthening happen in the same implementation wave or after context refactor stabilization?
   - **Decision: Same wave, after context refactor and before cleanup.** This is why Phase 8 (prompt/schema hardening) is sequenced after Phases 4-7 and before Phase 9 (cleanup).

## 13. Risk, Rollback, and Compatibility Strategy

- **Backward compatibility:** no *temporary* compatibility shims — no duplicate old/new module paths, no parallel file trees kept alive during migration, no re-export bridges added solely to avoid updating call sites. Every import site of a moved/renamed symbol is updated in the same change as the move, matching this codebase's established direct-cutover convention. This does **not** forbid the package's own stable `__init__.py` export surface (section 7's proposed structure keeps `answer_context/__init__.py` as the one import path consumers use) — that is the package's permanent public interface, not a migration-era compatibility shim, and Phase 2 is expected to preserve it.
- **Rollback unit:** each phase is scoped to be independently revertible — Phase 2's file split lands before Phase 3-8 add new behavior on top of it, so a problem discovered in, say, Phase 6 can be reverted without unwinding Phases 2-5. Do not squash multiple phases into one change; that is what makes the phase boundaries in section 10 meaningful.
- **Sequencing constraint:** Phases 3 through 8 assume Phase 2's model split has already landed (they add fields/types to files that Phase 2 relocates). Do not start Phase 4 before Phase 2 merges.
- **Blast radius:** contained to the question-answering and structured-retrieval answer-generation path (`answer_context/`, `answer_generation/`, `prompts/answer_generation/`, and the structured query-analysis files added to scope in 2.1). Ingestion, extraction, and other LangGraph nodes outside answer generation are not touched by this plan.
- **Test gate per phase:** each phase's exit criteria (where stated inline) and the traceability matrix (10.0) together define "done" for that phase — a phase is not complete until its mapped issue's `### Impact` bullets in section 4 no longer apply and its existing test suite (section 8.3) is green.

## 13.1 Reviewer Comments On This Latest Team Update

This version is much stronger than the earlier one. The added:

- traceability matrix
- adopted decisions section
- rollback / sequencing section

make it close to implementation-ready.

### Comment 1 - clarify the compatibility wording

There is still one wording conflict to resolve before implementation:

- Section 7 / Phase 2 assume stable package re-exports through `__init__.py`
- Section 13 says "no compatibility shims or re-export bridges"

These are compatible only if Section 13 means:

- no temporary duplicate old/new module paths
- no parallel file trees kept alive during migration
- but package-level `__init__.py` exports remain allowed as the stable import surface

That should be made explicit so the refactor does not stall on interpretation.

### Comment 2 - 4.3 remains the highest-urgency live correctness bug

The plan now maps the structured-context drop bug (4.3 / 9.7) to Phase 4, which is coherent from a design standpoint.

But from a production-risk standpoint, it is still the clearest live bug in this path:

- `structured_context` is successfully organized
- then discarded when no extra key-values are produced

So this should be treated as either:

- the first change inside Phase 4
- or an early micro-fix before the wider refactor if the team wants immediate risk reduction

### Comment 3 - Phase 2 must stay behavior-preserving in practice

Collapsing duplicated maintenance-reference representations in Phase 2 is sensible, but it must be executed as a behavior-preserving refactor:

- update formatter / merger / organizer consumers in the same change
- keep maintenance answer rendering identical at this stage
- defer answer-shape improvements to later phases

### Comment 4 - the observability move earlier is the right call

Moving diagnostics / rules-version parity earlier is a strong improvement.

That will make it much easier to tell whether later Phase 4 / 6 / 7 work:

- improves answer quality
- regresses extraction quality
- or changes formatting without improving grounding

### Comment 5 - the tree snippet should be normalized to ASCII

The package-structure proposal is good, but the tree block currently contains mojibake box-drawing characters (`â”œ`, `â”‚`, `â”€`, etc.).

That is only a documentation readability issue, not an architecture issue, but it should be cleaned before implementation starts so the structure can be copied safely.

## 13.2 Resolution Of Reviewer Comments

All five comments above are addressed as of this pass:

1. **Compatibility wording clarified.** Section 13's backward-compatibility bullet now explicitly distinguishes "no temporary migration-era shims/parallel trees" from "the package's own stable `__init__.py` export surface, which Phase 2 is expected to preserve." No conflict with section 7/Phase 2 remains.
2. **4.3/9.7 urgency elevated.** Phase 4 now states it is the first change in that phase, ahead of the typed-view work, and explicitly calls out that it can be pulled forward as a standalone micro-fix before Phase 2/3 if the team wants risk reduction sooner — it needs no new types, only removing the dead-path check. The traceability matrix (10.0) still shows it mapped to Phase 4 since that is where it will land by default; treat the micro-fix option as team discretion, not a doc inconsistency.
3. **Phase 2 behavior-preservation made explicit.** Added the three consumers that must move together (`MaintenanceEntryMerger`, `MaintenancePromptContextFormatter`, `AnswerContextOrganizer`), named the existing tests that must stay green with no assertion changes (`test_maintenance_entry_merger.py`, the maintenance-path tests in `test_answer_generation_service.py`), and explicitly deferred any answer-shape improvement to Phase 4+.
4. **Observability-ordering — no doc change needed;** this comment confirms the ordering already reflected in Phase 6 (verified: still correct, restated for confirmation).
5. **Tree snippet normalized to ASCII** (`|--`, `` `-- ``, `|` instead of Unicode box-drawing). Note for the record: the file's on-disk bytes were checked and were valid UTF-8 box-drawing characters, not actually corrupted — the mojibake was a rendering artifact in whatever viewer displayed it garbled. Normalizing to ASCII removes that fragility regardless of cause, since it renders identically in any editor/terminal/encoding.

## 14. Final Recommendation

The right upgrade path is not to patch the prompt builder again.

The right path is:

- enrich the answer-context model
- preserve structured semantics
- make format policy context-aware
- unify deterministic and LLM answer generation on the same typed context
- then remove the dead and low-value code that becomes unnecessary

That will move this area from "helpful prompt helper" to "enterprise answer-evidence layer".
