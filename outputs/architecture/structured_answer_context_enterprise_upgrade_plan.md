# StructuredAnswerContext Enterprise Upgrade Audit And Execution Plan

## Status

- **All 10 execution phases implemented.** See section 10 for the phase-by-phase plan and each phase's own `[IMPLEMENTED]`/`[PARTIALLY IMPLEMENTED]` status note with a "what was done vs. proposed" reconciliation.
- Final validation (Phase 10) confirmed: full `tests/unit` suite green at 2262 passed / 0 failed / 0 errors; `ruff --select F401,F841,F811` clean across the full touched subtree (`answer_context`, `answer_generation`, `prompts/answer_generation`, `prompts/common`).
- Two items remain deliberately open, not oversights — each has a documented reason in its own section: 4.8 (table evidence still simplified to one row grid — no additional data source identified), 4.9 (`AnswerSourceGroup`/`AnswerSectionGroup` still prompt-only — no renderer with a real grouping need found). Two items are partially implemented by deliberate scope decision: 4.6/9.6 (`limitation_note` added; `sections`/`reference_notes` deferred pending a guardrail-layer redesign).
- Original audit-only framing (below) is retained for history; treat every phase's own status note as the current source of truth over this top-level summary.

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

**Resolved in Phase 4:** `AnswerStructuredEntity`/`AnswerRelationship` now preserve relationships as typed objects (source/target entity type, relationship type, confidence, direction, and the target's own fields) instead of flattening them into `AnswerKeyValue` immediately. `AnswerKeyValue` extraction still runs in parallel unchanged, per Decision #2 — this is additive, not a replacement.

## 4.3 Structured context is sometimes built and then dropped

If structured entities/identifiers exist but do not produce extra key-values, `_join_structured_facts()` returns `None` for `structured_context`:

- `src/application/workflows/question_answering/question_answering_workflow.py:531-532` (line numbers corrected in this amendment — see section 0)

### Impact

- some answer-context work becomes dead-on-arrival
- typed maintenance entries, groups, and diagnostics can be lost even though prepared chunks existed
- this is not just a style issue; it is a behavior gap

**Resolved in Phase 4.** The dead-path early return was removed; `structured_context` is now always returned once it was successfully organized, regardless of whether `extra_key_values` ended up empty. The baseline test that characterized the old behavior (`test_resolved_structured_entities_without_lookup_service_do_not_crash`) was updated to assert the corrected behavior instead.

## 4.4 `AnswerFormatPolicy.resolve()` is not really resolving anything yet

Current code:

- `src/application/services/answer_generation/formatting/answer_format_policy.py:33-40`

It accepts `structured_context`, then ignores it:

- line 39: `_ = structured_context`

### Impact

- format policy is intent-only, not evidence-aware
- table-rich answers, sparse answers, multi-document answers, contact-heavy answers, and maintenance-summary answers cannot choose the best output policy from real context

This is a confirmed low-value path and a strong dead-code candidate for cleanup/replacement.

## 4.5 Prompt construction still depends on flattened lists instead of typed context views [IMPLEMENTED in Phase 8]

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

## 4.6 LLM schema is too weak for enterprise answer generation [PARTIALLY IMPLEMENTED in Phase 8]

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

## 4.7 Deterministic renderers are useful but fragmented [IMPLEMENTED in Phase 7]

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

## 4.12 A dead configuration knob with a live divergence risk if ever wired up [RESOLVED in Phase 1]

`AnswerGenerationRequest.max_context_chunks` is declared and checked, but no production caller ever sets it.

References:

- `src/application/services/answer_generation/answer_generation_request.py` (field declaration)
- `src/application/services/answer_generation/answer_generation_service.py` (`_resolve_request`: `if request.max_context_chunks is not None: context_chunks = context_chunks[: request.max_context_chunks]`)

### Impact

- this is the exact seam that made the pre-amendment double-intent-computation bug (section 0.1) a live risk rather than a theoretical one: if a future caller sets `max_context_chunks` to cap prompt size, the truncated `context_chunks` would only affect `AnswerGenerationService`'s own fallback `analyze()` path (when no `answer_intent_decision` was passed) — a caller that both sets `max_context_chunks` *and* relies on the fallback recompute could still get a different intent than whatever built `structured_context` upstream
- whoever wires this up next should be aware of that interaction, not just the truncation itself

**Resolved:** removed in Phase 1 rather than kept-and-redesigned (both field and truncation branch deleted; zero production callers existed, so this was a pure subtraction with no behavior change for any real caller). See Phase 1's status note for the full rationale.

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

## 4.16 A resolved `MaintenanceTask -> Procedure` relationship's `steps` are silently dropped before reaching the answer (found during Phase 2, missed in original audit) [RESOLVED in Phase 4]

`MaintenanceTask` (`src/domain/extraction/maintenance_task.py:8-26`) has no `steps` field of its own — only `title`, `description`, `interval`, `component_name`, `equipment_id`. `Procedure` (`src/domain/extraction/procedure.py:36`) does: `steps: list[str]`. The two are linked by `SemanticRelationshipType.TASK_USES_PROCEDURE` (`src/domain/extraction/semantic_relationship.py:31`), populated by proximity-based candidate generation (`src/application/workflows/linking/semantic_relationship_candidate_generator.py:26-29`).

That relationship is resolved correctly: `StructuredEntityResolver._attach_related_entities()` (`src/application/workflows/retrieval/structured/structured_entity_resolver.py:118-204`) does stitch the full related `Procedure` dict — including its populated `steps` — onto a resolved `MaintenanceTask`'s `related_entities` list. The data genuinely reaches the structured-evidence layer.

It is then dropped one hop later. `StructuredFactKeyValueBuilder._ENTITY_FIELD_LABELS` (`src/application/workflows/question_answering/answer_context/structured_fact_key_value_builder.py:8-39`) has entries for `manufacturer`, `supplier`, `spare_part`, `equipment`, `maintenance_task`, and `contact_point` — but no `"procedure"` key. `_iter_entities_with_related()` generically walks every related entity (so the linked Procedure does flow through), but `_field_labels_for_entity()` only special-cases `contact_point`; for `entity_type="procedure"` it falls through to `_ENTITY_FIELD_LABELS.get("procedure", ())`, an empty tuple. The steps are structurally present in the payload and never mapped to any label/value, so they never become an `AnswerKeyValue`.

Separately, the raw-text extraction path has no steps concept at all: `KeyValueExtractor.extract_maintenance_entries()` (`_maintenance_candidate_from_line`, `_maintenance_candidate_from_table_row`) always produces exactly one atomic task per line/row — it never groups a multi-line numbered sequence under one task as a step list. Confirmed at the prompt level too: `maintenance_task_extraction_schema.py` has no `steps` key; `procedure_extraction_schema.py` explicitly requires one. Steps are a Procedure-only concept everywhere in this codebase except the one relationship that connects them to a task.

### Impact

- a user asking "how do I do `<maintenance task X>`?" gets no step-by-step answer even when the document's extraction pipeline successfully identified and linked the exact procedure that answers the question — the link exists, resolves, and is thrown away one layer before the answer
- two independent gaps, not one: (a) the structured-resolution path drops already-linked steps at a single missing map entry (small, mechanical fix), and (b) the raw-text path has no step-list concept in `AnswerMaintenanceEntry` at all (a real modeling question — `AnswerKeyValue.value` is a single string, so "steps" doesn't fit that shape without a list-valued view, which is exactly what Phase 4's typed structured-evidence views are for)
- natural fix location is Phase 4 (`procedure_entries`/`relationship_views`, section 9.2/9.3), not a Phase 2/3 patch — this is the same *shape* of bug as 4.3 (resolved data silently discarded before reaching the answer), just at the field level instead of the whole-context level, and it is exactly the kind of relationship section 9.3 already describes preserving

**Resolved:** sub-fix (a) is done — `steps` now survives via `AnswerRelationship.target_entity_fields["steps"]` (see `test_build_preserves_related_procedure_steps_through_relationship` and the workflow-level `test_resolved_maintenance_task_surfaces_linked_procedure_steps_end_to_end`). Sub-fix (b) (whether `AnswerMaintenanceEntry`'s raw-text path should ever gain step-grouping) is deliberately left open — not resolved as a side effect of this fix, per this finding's own framing.

## 4.17 A third write-only field, same shape as 4.11 (found during Phase 6, missed in original audit) [RESOLVED in Phase 9]

`AnswerFormatPolicy.include_sources_inline` is declared on every one of the 10 `_POLICIES` entries (`src/application/services/answer_generation/formatting/answer_format_policy.py`), always hardcoded to `False`, and never read by `AnswerPromptBuilder._format_policy_block()` (`src/application/prompts/answer_generation/answer_prompt_builder.py:83-100`) — unlike `preferred_format`, `response_label`, `include_bullets`, `include_steps`, `include_table`, `max_bullets`, and `instruction_lines`, which are all rendered into the prompt. Found while implementing Phase 6's context-aware `resolve()`, when checking whether this field was a safe delivery mechanism for the new `is_multi_document` signal — it is not, since writing to a field nothing reads would just be a second instance of exactly what 4.11/9.9 already flagged for the confidence fields.

### Impact

- identical shape to 4.11: a field is threaded through every policy construction for a purpose (presumably: render source citations inline within the answer body rather than only as trailing citations) that was never implemented downstream
- low risk today (defaults to `False` everywhere, so it's inert rather than actively wrong), but the same "whoever wires this up next needs to decide if it means anything" caution from 4.11 applies

**Not resolved in Phase 6, not resolved in Phase 7** — Phase 6 deliberately flagged rather than fixed it; Phase 7 investigated and confirmed wiring it up for real (building an actual inline-citation renderer capability) was new feature work, not a unification of an existing dual-representation, so out of scope there too. **Resolved in Phase 9**: since no phase in this plan intends to build that feature, and the field is confirmed to have zero readers, removed the field entirely (`include_sources_inline` deleted from `AnswerFormatPolicy` and all 10 `_POLICIES` entries) rather than leaving a permanently-dead field in place. If inline citation rendering is wanted later, it should be designed and added with its actual consumer in the same change, not resurrected as an empty field first.

## 4.18 Two more write-only fields on `AnswerGenerationRequest` (found during Phase 9, missed in original audit)

`AnswerGenerationRequest.document_id` and `.require_citations` were both set at the request's one production construction site (`QuestionAnsweringWorkflow._resolve_and_generate` — passed as `document_id=request.document_id, require_citations=request.require_citations`) but never read anywhere in `AnswerGenerationService`, `AnswerPromptBuilder`, or either deterministic renderer. Found while sweeping the `answer_generation` subtree for dead code per Phase 9's charter.

- `require_citations` in particular reads as though it should gate citation enforcement, but the actual citation-enforcement guardrail (`citation_guardrail.py`/`answer_guardrail_policy.py`) has its own, completely separate `require_citations` config sourced from `guardrail_settings` — the two never connect. `AnswerGenerationRequest.require_citations` was a dead duplicate of a concept implemented elsewhere.
- `document_id` is likewise redundant with real, used fields: `AnswerSource.document_id`/`.document_title` (Phase 3) already carry per-source document identity into the typed context.

### Impact

- same shape as 4.11/4.17: fields threaded through construction for an apparent purpose that was never wired to a real consumer
- zero test coverage depended on either field's downstream behavior (confirmed before removal)

**Resolved in Phase 9**: both fields removed from `AnswerGenerationRequest`, and their assignment removed from the one construction call site in `question_answering_workflow.py`. Pure subtraction — no production caller or test relied on either field being read.

## 5. Dead Code / Low-Value Path Review

## 5.1 Confirmed low-value or dead-path behavior

### A. `AnswerFormatPolicy.resolve(..., structured_context=...)` [RESOLVED in Phase 6]

- Parameter is accepted but ignored.
- This should either become a real resolver or be removed/replaced.
- ✅ Resolved in Phase 6 — see 4.4/9.4. `resolve()` now derives real context signals and is no longer a no-op.

Reference:

- `src/application/services/answer_generation/formatting/answer_format_policy.py:33-40`

### B. Structured context creation can be discarded when no extra key-values are produced [RESOLVED in Phase 4]

- This is a dead-path behavior, not a dead file.
- Resolved in Phase 4 (see 4.3) — the dead-path return was removed.

Reference:

- `src/application/workflows/question_answering/question_answering_workflow.py:531-532` (line numbers corrected in this amendment — see section 0)

### C. Prompt-only grouping models

- `AnswerSourceGroup` and `AnswerSectionGroup` are not dead, but currently underused and likely need redesign or stronger consumers.

### D. `AnswerKeyValue.confidence` / `AnswerMaintenanceEntry.confidence` (missed in original audit) [RESOLVED in Phase 6]

- Written on every construction, never read anywhere in `src/`.
- See section 4.11.
- ✅ `AnswerMaintenanceEntry.confidence` removed (confirmed zero possible variance — always exactly `0.88`). `AnswerKeyValue.confidence` kept and wired into `AnswerFormatPolicy`'s `has_low_confidence_evidence` signal (confirmed a real variable value from `StructuredFactKeyValueBuilder`'s domain-derived producer, unlike the maintenance-entry field).

Reference:

- `src/application/workflows/question_answering/answer_context/structured_answer_context.py:49`, `:66`

### E. `AnswerGenerationRequest.max_context_chunks` (missed in original audit) [RESOLVED in Phase 1: removed]

- Declared and checked, never set by the one production caller (`QuestionAnsweringWorkflow`).
- See section 4.12 for why this is not just inert — it is the seam that made the pre-amendment double-intent-computation bug reachable.
- Removed rather than kept: zero production callers, so deleting it was a pure subtraction.

Reference:

- `src/application/services/answer_generation/answer_generation_request.py`

## 5.2 Removal candidates after replacement exists [EVALUATED in Phase 9 -- none applicable]

These should not be deleted immediately. They should be removed only after the new typed answer-context path is in place:

- prompt-only string grouping blocks if replaced by typed answer views — **not applicable**: `source_groups`/`section_groups` were never replaced by a typed view that supersedes them (4.9 remains open per Phase 7's decision), so there is nothing to remove here yet.
- ad-hoc field-label flattening that becomes redundant once typed answer sections exist — **not applicable**: Phase 8 added typed `structured_entities` serialization to the prompt, but per 4.2's explicit, repeatedly-reaffirmed design decision, `AnswerKeyValue` flattening runs *in parallel*, not as something the typed view replaces. The flattening was never intended to become redundant.
- duplicated spare-parts / identifier formatting branches if moved behind a unified rendering policy layer — **not applicable**: Phase 7 unified both renderers onto the same typed input model (`AnswerSource`/`key_values`) without needing a shared rendering-policy abstraction. The two renderers format structurally different content (tabular rows vs. grouped identifier lists); forcing them behind one shared branch would be an arbitrary abstraction with no real duplication to remove.

All three candidates were evaluated during Phase 9 and found inapplicable — their preconditions never materialized, by design, not by oversight.

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

## 9.1 Expand the answer source model instead of re-deriving metadata later [IMPLEMENTED in Phase 3]

Add answer-facing fields for:

- ✅ `retrieval_source`
- ✅ `section_id`
- ✅ `statistics`
- ✅ `identifier_values`
- ✅ `metadata`
- `table_ids` — **not implemented; not currently reachable.** `AnswerSource`'s only input is `RetrievedChunk`, which has no `table_ids` field and nothing threads one into its `metadata` dict consistently (only a `hydrated_table_ids` metadata key exists, and only for chunks that went through `TableEvidenceHydrator`). Surfacing this for real would mean enriching `RetrievedChunk` itself first — a retrieval-layer change, out of scope for this answer-context plan. The general `metadata` passthrough above already gives ad-hoc access to `hydrated_table_ids` where it exists.
- `picture_ids` — **not implemented; not currently reachable at all.** Nothing in the codebase produces this value anywhere on `RetrievedChunk` or its metadata. A field with no data source would always read empty — not added.
- `chunk_index` / `chunk_total` — **not implemented; not currently reachable.** These are `DocumentChunk` (ingestion-layer) fields, not `RetrievedChunk` (retrieval-layer, `AnswerSource`'s actual input) fields, and nothing threads them across during retrieval.
- ✅ `family_key` or equivalent split-family reference — implemented as `collapsed_chunk_ids: list[str]`, decoded from `metadata["dedup_collapsed_chunk_ids"]` (already set by `RetrievedChunkDeduplicator` and already consumed elsewhere in `question_answering_workflow.py`) rather than inventing a new mechanism.

This should be a direct, clean answer-facing projection, not a copy of the whole chunk model.

**Correction to this list found during implementation:** four of the nine originally-proposed fields (`table_ids`, `picture_ids`, `chunk_index`, `chunk_total`) were written against `DocumentChunk`'s field list without checking that `AnswerSource` is actually built from `RetrievedChunk` — a narrower, retrieval-layer dataclass that doesn't carry them. Implementing them as real fields would have meant either fabricating always-empty fields or first enriching `RetrievedChunk` itself (a different, bigger initiative). `family_key` was resolved by finding the codebase's own existing equivalent (`dedup_collapsed_chunk_ids`) rather than designing a new one.

## 9.2 Introduce first-class structured evidence views [IMPLEMENTED in Phase 4, redesigned]

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

**Implemented as one generic `AnswerStructuredEntity` type (with a string `entity_type` field) inside `StructuredAnswerContext.structured_entities`, plus `entities_of_type(entity_type)` for filtering — not as 10 separately-named fields.** `certification_entries` has no data source anywhere in this codebase (no `CERTIFICATION` member on `StructuredEntityType`) and would have been a permanently-empty field; `table_evidence`/`asset_evidence` have no identified data source beyond what Phase 3's `AnswerSource.table_rows` already exposes per-source, so both are deferred rather than added speculatively (see 4.8, still open). The other 7 categories are all reachable today via `entities_of_type("procedure")`, `entities_of_type("specification")`, etc.

## 9.3 Preserve structured relationships [IMPLEMENTED in Phase 4]

Add answer-context types that preserve:

- ✅ source entity type — the owning `AnswerStructuredEntity.entity_type`
- ✅ target entity type — `AnswerRelationship.target_entity_type`
- ✅ relationship type — `AnswerRelationship.relationship_type`
- ✅ confidence — `AnswerRelationship.confidence_score`
- ✅ direction — `AnswerRelationship.direction`
- ✅ source chunk references — `AnswerStructuredEntity.source_chunk_id`, plus the target's own source chunk id inside `target_entity_fields`

This will let the answer layer generate cleaner manufacturer/contact, equipment/specification, and procedure/warning answers. Confirmed working for the procedure/task case (4.16); manufacturer/contact and equipment/specification use the exact same mechanism since `StructuredEntityResolver` attaches all relationship types identically, but no dedicated test covers those specific pairs yet — only 4.16's task/procedure case was directly exercised in this phase.

## 9.4 Make format-policy resolution real [IMPLEMENTED in Phase 6]

`AnswerFormatPolicy.resolve()` should use:

- answer intent
- evidence density
- presence of tables
- presence of typed entries
- presence of structured relationships
- whether evidence is single-document vs mixed

This turns policy from static lookup into real answer orchestration.

✅ Done — implemented as four signals (`is_sparse_evidence`, `has_low_confidence_evidence`, `has_rich_structured_evidence`, `is_multi_document`), with "presence of tables"/"presence of typed entries"/"presence of structured relationships" combined into the single `has_rich_structured_evidence` check rather than three separate ones. See Phase 6's status note for the full design reasoning and the combined-check justification.

## 9.5 Unify deterministic rendering on top of the same typed context [PARTIALLY IMPLEMENTED in Phase 7]

Do not remove deterministic renderers.

Instead:

- keep deterministic rendering for high-confidence, structured answer types
- make them consume the same enriched `StructuredAnswerContext`
- avoid custom parsing branches where the answer context already knows the facts

✅ Done for `AnswerSource`-level consumption: both renderers now consume `StructuredAnswerContext` (via `sources`/`key_values`) instead of raw `RetrievedChunk`/duplicated parsing. Not done for group-level consumption (`AnswerSourceGroup`/`AnswerSectionGroup`, 4.9) or `include_sources_inline` (4.17) — both investigated and left open with reasoning in Phase 7's status note, since forcing either would have been cosmetic churn or a new feature rather than a real unification.

## 9.6 Strengthen the answer-generation schema [PARTIALLY IMPLEMENTED in Phase 8]

The LLM response schema should evolve from:

- `answer_text`

to something closer to:

- `answer_text`
- `limitation_note`
- `sections`
- `reference_notes`

This does not mean exposing raw internal ids. It means enforcing answer structure instead of leaving everything to prose.

✅ `limitation_note` added (optional, `GeneratedAnswer.limitation_note`). `sections`/`reference_notes` deferred — every current consumer of `GeneratedAnswer.answer_text` (5 guardrails, the answer-question tool, the QA workflow) is built around one flat answer string; adding either field now would be unconsumed until those consumers are redesigned to work over structured sections instead of prose, which is separate, larger follow-up work. See Phase 8's design note.

## 9.7 Stop dropping structured context [IMPLEMENTED in Phase 4]

`QuestionAnsweringWorkflow._join_structured_facts()` should keep the structured context whenever it was successfully built, not only when extra key-values exist.

That is a correctness upgrade, not just a cleanup. ✅ Done — the dead-path early return was removed; `structured_context` is now always returned once organized.

## 9.8 Close the enum-exhaustiveness gap (added in this amendment)

Add a parametrized test iterating every `AnswerIntent` member and asserting it has an entry in `AnswerFormatPolicy._POLICIES`, and treat `_CHUNK_TYPE_TO_INTENT`/`_RETRIEVAL_INTENT_TO_ANSWER_INTENT` as intentionally partial mappings (not every intent needs a chunk-type or retrieval-intent trigger) — but document that distinction explicitly rather than leaving it implicit. See 4.15.

## 9.9 Retire or recalibrate the decorative confidence fields (added in this amendment) [IMPLEMENTED in Phase 6]

Before section 9.2/9.3 add new typed evidence views, decide whether `AnswerKeyValue.confidence`/`AnswerMaintenanceEntry.confidence` are worth keeping. Either wire them into something that reads them (a low-confidence-evidence warning in the format policy, for instance - which would also give 9.4's context-aware policy work a concrete first signal to consume) or remove them rather than propagating an uncalibrated number into whatever the new typed views become. See 4.11.

✅ Done, decided each field independently rather than treating them as one decision — `AnswerMaintenanceEntry.confidence` removed (traced to a single producer that always assigns exactly `0.88`, zero variance ever possible, purely decorative); `AnswerKeyValue.confidence` kept and wired into `AnswerFormatPolicy`'s new `has_low_confidence_evidence` signal exactly as this section's own example suggested, since it carries a real variable domain-derived value via `StructuredFactKeyValueBuilder`. See Phase 6's status note.

## 9.10 Add rules-version constants and diagnostic counts to the formatting layer (added in this amendment) [IMPLEMENTED in Phase 1 + Phase 6]

Mirror the `*_RULES_VERSION` + structured-logging pattern already used by `AnswerIntentAnalyzer`/`RetrievalQueryIntentInferer` on `AnswerFormatPolicy`, `KeyValueExtractor`, and `MaintenanceEntryMerger`. Surface `SparePartsTableParser`'s existing `dropped_row_count`/`partial` tracking as a queryable diagnostic (matching how every other stage in this pipeline reports through a `diagnostics` dict) instead of only a one-line notice in the rendered answer text. This should land first as baseline instrumentation in Phase 1, then be consumed and extended by the richer format-policy work in Phase 6. See 4.14.

✅ Baseline (`*_RULES_VERSION` constants, `spare_parts_dropped_row_count`/`spare_parts_partial` diagnostics) done in Phase 1. Consumption/extension done in Phase 6: `AnswerFormatPolicy.resolve()` now logs `answer_format_policy_context_adjusted` (mirroring `AnswerIntentAnalyzer`'s `answer_intent_resolved` line shape) whenever a context signal fires, and `ANSWER_FORMAT_POLICY_RULES_VERSION` was bumped `v1 -> v2` to reflect `resolve()`'s materially new behavior.

## 10. Execution Plan For Review

### 10.0 Traceability Matrix

Every issue in sections 4 and 5, and every solution in section 9 (including the reviewer's four adjustments in section 0.1), maps to exactly one phase below. Nothing found in this audit is left without an assigned remediation phase.

| Issue | Phase(s) | Solution ref |
|---|---|---|
| 4.1 `AnswerSource` too thin | Phase 3 — **done** (5 of 9 proposed fields; 4 not reachable, see 9.1) | 9.1 |
| 4.2 structured semantics flattened too early | Phase 4 — **done** | 9.2, 9.3 |
| 4.3 / 5.1.B structured context sometimes dropped | Phase 4 — **done** | 9.7 |
| 4.4 / 5.1.A `AnswerFormatPolicy.resolve()` ignores context | Phase 6 — **done** | 9.4 |
| 4.5 prompt depends on flattened lists | Phase 8 — **done** (`structured_entities`/relationships now serialized) | 9.6 |
| 4.6 LLM schema too weak | Phase 8 — **partially done** (`limitation_note` added; `sections`/`reference_notes` deferred, see Phase 8's design note) | 9.6 |
| 4.7 deterministic renderers fragmented | Phase 7 — **done** | 9.5 |
| 4.8 table evidence partially modeled | Phase 4 — **still open**, `table_evidence`/`asset_evidence` deferred (no additional data source identified, see Phase 4's design note) | 9.2 (`table_evidence`) |
| 4.9 groups are prompt-facing only | Phase 7 — investigated, **still open** (no renderer with a real grouping need found; see Phase 7's "Not addressed" note) | 9.5 |
| 4.10 tests lock in the limited model | Phase 1, Phase 10 | section 11 |
| 4.11 / 5.1.D dead `confidence` fields | Phase 6 — **done** (`AnswerMaintenanceEntry.confidence` removed — zero variance ever possible; `AnswerKeyValue.confidence` kept and wired into `has_low_confidence_evidence`, since it carries a real domain-derived signal via `StructuredFactKeyValueBuilder`) | 9.9, reviewer 0.1 #4 |
| 4.12 / 5.1.E dead `max_context_chunks` | Phase 1 — **done** (removed) | reviewer 0.1 #1 |
| 4.13 redundant maintenance-entry data model | Phase 2 — **done** | reviewer 0.1 #2 |
| 4.14 no rules-version / observability parity | Phase 1 — **done**, Phase 6 — **done** (consumption: `format_policy_context_signals` diagnostic, `ANSWER_FORMAT_POLICY_RULES_VERSION` bumped to v2) | 9.10, reviewer 0.1 #3 |
| 4.15 no `AnswerIntent` exhaustiveness guard | Phase 1 — **done** | 9.8 |
| 4.16 `task_uses_procedure` steps silently dropped | Phase 4 — **done** | 9.2, 9.3 |
| 4.17 dead `include_sources_inline` field (found in Phase 6) | Phase 9 — **done** (removed; no phase intends to build the inline-citation feature it was reserved for) | 9.5 |
| 4.18 dead `document_id`/`require_citations` fields on `AnswerGenerationRequest` (found in Phase 9) | Phase 9 — **done** (removed, pure subtraction) | — |

## Phase 1 - Baseline protection [IMPLEMENTED]

- add an audit snapshot test plan for current behavior — satisfied by the existing suite listed in section 2 ("Tests currently covering this area"); no material gap found
- add coverage around current `StructuredAnswerContext` construction — already covered by `test_answer_context_organizer.py`; no material gap found
- add regression tests around structured-entity joining and structured-context retention — already covered by the structured-fact-joining tests in `test_question_answering_workflow.py` (including `test_resolved_structured_entities_without_lookup_service_do_not_crash`, which characterizes the current context-drop behavior from 4.3/9.7 as a baseline for Phase 4 to change)
- ✅ add/keep regression coverage for pre-resolved `answer_intent_decision` reuse — `test_generate_skips_recomputing_intent_when_decision_is_already_resolved`, `test_generate_still_computes_intent_when_no_decision_is_provided` (`test_answer_generation_service.py`), `test_answer_intent_is_resolved_exactly_once_when_structured_facts_are_joined` (`test_question_answering_workflow.py`)
- ✅ add the `AnswerIntent` exhaustiveness guard tests called out in 9.8 — `test_every_answer_intent_has_a_dedicated_format_policy_entry` (`test_answer_format_policy.py`)
- ✅ **decision made:** `AnswerGenerationRequest.max_context_chunks` is **removed**, not kept-and-redesigned. Rationale: zero production callers, already flagged as dead code (4.12/5.1.E), and its only real effect was being the seam behind the now-fixed double-intent-computation bug. Removing it is strictly simpler than designing a canonical truncation point for a feature nothing uses; if per-request context capping is genuinely needed later, it can be reintroduced with a real design at that point. Removed the field from `AnswerGenerationRequest` and the truncation branch from `AnswerGenerationService._resolve_request()`. This also simplifies Phase 3 below (its conditional bullet is removed) and closes out 4.12/5.1.E.
- [done] add baseline rules-version constants and diagnostics parity on the current formatting path before structural refactors begin - added `ANSWER_FORMAT_POLICY_RULES_VERSION`, `KEY_VALUE_EXTRACTOR_RULES_VERSION`, `MAINTENANCE_ENTRY_MERGER_RULES_VERSION`, `SPARE_PARTS_TABLE_PARSER_RULES_VERSION`; the first three are surfaced in `GeneratedAnswer.diagnostics` via `AnswerGenerationService._build_diagnostics()`, and the fourth is surfaced through `SparePartsListRenderer.last_diagnostics()` / deterministic-answer diagnostics when that renderer is used. Covered by `test_generate_diagnostics_include_formatting_layer_rules_versions`.
- [done] surface table-parser partial/drop counts as structured diagnostics on the current path - `SparePartsGroup` carries `dropped_row_count` and `partial`, `SparePartsListRenderer.last_diagnostics()` now exposes both as `spare_parts_dropped_row_count` and `spare_parts_partial`, and `AnswerGenerationService` merges them into `GeneratedAnswer.diagnostics` whenever the spare-parts renderer produces the answer. Covered by `test_last_diagnostics_reports_dropped_row_count_after_partial_parse`, `test_last_diagnostics_reports_zero_when_no_rows_are_dropped`, `test_last_diagnostics_resets_to_zero_for_unsupported_intent`, and the deterministic spare-parts path assertion in `test_answer_generation_service.py`.

Full regression: 236 tests green across `tests/unit/application/services/answer_generation/`, `tests/unit/application/workflows/question_answering/`, `tests/unit/application/guardrails/`.

## Phase 2 - Model refactor [IMPLEMENTED]

- ✅ split `structured_answer_context.py` into smaller answer-context model files — new `answer_context/models/` subpackage: `answer_source.py` (`AnswerSource`), `answer_groups.py` (`AnswerSourceGroup`, `AnswerSectionGroup`), `answer_key_value.py` (`AnswerKeyValue`), `answer_maintenance_entry.py` (`AnswerMaintenanceEntry`, `AnswerMaintenanceReference`), `structured_answer_context.py` (`StructuredAnswerContext`). Old monolithic `answer_context/structured_answer_context.py` deleted (no shim), matching section 13's direct-cutover convention.
- ✅ keep `src.` imports and stable re-exports — `answer_context/__init__.py` still re-exports every model name unchanged; only its own internal import source moved from the deleted file to `.models`. External consumers now import from the package root (`...answer_context import X`) instead of the specific deleted submodule; internal package files (`key_value_extractor.py`, `maintenance_entry_merger.py`, `structured_fact_key_value_builder.py`, `answer_context_organizer.py`, `source_group_builder.py`, `section_group_builder.py`) import directly from the sibling `.models` package. All 15 import sites found via repo-wide search were updated in this same change.
- [done] collapse `AnswerMaintenanceEntry`'s duplicated reference representations - `page_start`, `page_end`, `section_path`, `source_numbers`, `section_paths` are no longer separate stored fields; they are now `@property` accessors derived from `references` (the single source of truth). Only `source_number` remains a real field (the primary/first source, matching `AnswerKeyValue.source_number`'s own convention), auto-populated into a single-item `references` list via `__post_init__` when a caller does not pass `references` explicitly. As a follow-up hardening step during review, `__post_init__` now also canonicalizes `source_number` from the first explicit reference when `references` are provided, so the scalar primary-source field cannot drift out of sync with the provenance list.
- [done] do not change answer behavior yet beyond structural cleanup and removal of duplicated internal representations - confirmed by the existing maintenance-path tests plus added direct coverage for the package-root re-export surface (`test_answer_context_exports.py`), the `AnswerMaintenanceEntry` invariants (`test_answer_maintenance_entry.py`), and the maintenance formatter's use of reference-derived page/section/source data after the refactor (`test_maintenance_prompt_context_formatter.py`).
- **Correction to this phase's original consumer list:** the plan named `AnswerContextOrganizer` as one of three consumers needing changes. On inspection, `AnswerContextOrganizer.organize()` only ever reads `entry.interval` (for a diagnostics count) — it never touches `references`/`source_numbers`/`page_start`/`section_path`, so it needed zero changes. The actual third consumer (alongside `MaintenanceEntryMerger` and `MaintenancePromptContextFormatter`) is `KeyValueExtractor.extract_maintenance_entries()`, which is where entries are originally constructed. Also found and removed during the collapse: `MaintenanceEntryMerger._merge_ordered_ints()`, `_merge_ordered_strings()`, `_min_page()`, `_max_page()` — four private helpers that existed solely to maintain the now-removed duplicate fields, dead the moment those fields were removed.

Full regression: 2220 tests green across the entire `tests/unit` suite (not just the affected area — full-suite run, since this phase touches import paths reachable from many packages).

## Phase 3 - Source enrichment [IMPLEMENTED]

- ✅ enrich `AnswerSource` projection with missing retrieval/chunk metadata — added `retrieval_source`, `section_id`, `statistics`, `identifier_values`, `metadata` (direct passthrough from `RetrievedChunk`) and `collapsed_chunk_ids` (decoded from the existing `dedup_collapsed_chunk_ids` metadata convention). See 9.1 for the 4 originally-proposed fields found not to be reachable from `RetrievedChunk` and why.
- ✅ update organizer tests — `test_context_organizer_enriches_source_with_retrieval_metadata`, `test_context_organizer_defaults_collapsed_chunk_ids_when_not_deduplicated` added to `test_answer_context_organizer.py`
- ✅ ensure no consumer breaks — full suite green (2222/2222); no consumer of `AnswerSource` reads the new fields yet, so this phase is purely additive

Full regression: 2222 tests green across the entire `tests/unit` suite.

## Phase 4 - Typed structured-evidence views [IMPLEMENTED]

- ✅ **First change in this phase:** `QuestionAnsweringWorkflow._join_structured_facts()` now retains the built `structured_context` unconditionally once it was successfully organized (closes 4.3/9.7 and 5.1.B). The dead-path early return (`if not extra_key_values: return prepared_chunks, None, intent_decision`) was removed entirely.
- ✅ add first-class answer models for structured entities, relationships, tables, and assets — added `AnswerStructuredEntity` and `AnswerRelationship` (`answer_context/models/answer_structured_entity.py`, `answer_relationship.py`) and a new `StructuredEvidenceViewBuilder` (`answer_context/structured_evidence_view_builder.py`) that converts the raw resolved-entity dicts into these typed views. `StructuredAnswerContext` gained `structured_entities: list[AnswerStructuredEntity]` plus an `entities_of_type(entity_type)` filter method.
- ✅ keep `AnswerKeyValue` as a convenience projection, not the only structured view — `StructuredFactKeyValueBuilder` is untouched and still runs in parallel on the same `resolved_structured_entities` input; `AnswerKeyValue` output is unchanged.
- ✅ closes 4.16 — a resolved `task_uses_procedure` relationship's target entity (the linked `Procedure`, including its `steps` list) now survives as `AnswerRelationship.target_entity_fields["steps"]` on the owning `AnswerStructuredEntity`, instead of being dropped by `StructuredFactKeyValueBuilder`'s missing `"procedure"` label-map entry. Sub-fix (b) (whether `AnswerMaintenanceEntry`'s raw-text path should gain step-grouping) remains an open, deliberately-deferred modeling question — not resolved here, since steps are now reachable via the structured-resolution path, which is the primary path for this data.

**Design note on scope, found during implementation:** section 9.2 proposed 10 separately-named typed collections (`specification_entries`, `procedure_entries`, `troubleshooting_entries`, `safety_entries`, `contact_entries`, `equipment_entries`, `certification_entries`, `table_evidence`, `asset_evidence`, `relationship_views`). Implemented instead as one generic `structured_entities: list[AnswerStructuredEntity]` list (typed by a string `entity_type` field) plus `entities_of_type()` for filtering, rather than 10 separately-populated fields. Reasons: (1) no separate storage to drift out of sync — a consumer wanting "procedure entries" calls `entities_of_type("procedure")` against the one real list; (2) `certification_entries` has no data source at all in this codebase (`StructuredEntityType` has no `CERTIFICATION` member — there is no structured-extraction path for certifications), so a dedicated field would be permanently empty, repeating the exact "dead field" mistake already found and corrected in 4.11/4.12/9.1; (3) `table_evidence`/`asset_evidence` have no clearly-identified *additional* data source beyond what `AnswerSource.table_rows` (Phase 3) already exposes per-source — deferred rather than added speculatively. `relationship_views` is implemented as `AnswerStructuredEntity.relationships: list[AnswerRelationship]` (attached per-entity, matching how `StructuredEntityResolver` itself attaches them) rather than a separate flat list.

Full regression: 2235 tests green across the entire `tests/unit` suite. New tests: `test_structured_evidence_view_builder.py` (5 tests, including a direct regression test for 4.16's procedure-steps preservation), `test_resolved_maintenance_task_surfaces_linked_procedure_steps_end_to_end` (workflow-level end-to-end 4.16 coverage), and the corrected `test_resolved_structured_entities_without_lookup_service_do_not_crash` (now asserts `structured_context is not None`, closing the 4.3/9.7 baseline gap that test was tracking).

## Phase 5 - Organizer redesign [IMPLEMENTED]

- ✅ keep `AnswerContextOrganizer` as orchestration only — audited `organize()` after Phase 4 and found exactly one piece of real extraction/mapping logic still embedded directly in it: `_to_source()` plus its two static helpers (`_decode_collapsed_chunk_ids()`, `_decode_table_rows()`), mapping a `RetrievedChunk` into an `AnswerSource`. Everything else `organize()` does was already delegation to `KeyValueExtractor`, `MaintenanceEntryMerger`, `SourceGroupBuilder`, `SectionGroupBuilder`.
- ✅ move extraction logic into focused builders/extractors — moved `_to_source()`/`_decode_collapsed_chunk_ids()`/`_decode_table_rows()` verbatim (no behavior change) into a new `StructuredSourceBuilder` class (`answer_context/structured_source_builder.py`, matching the file name section 7's proposed tree already used for this exact responsibility). `AnswerContextOrganizer` now takes a `structured_source_builder: StructuredSourceBuilder | None = None` constructor param (defaulting to `StructuredSourceBuilder()`) and its `organize()` first line is `sources = self.structured_source_builder.build_sources(chunks)`. Wired into the package's lazy `__getattr__` export pattern in `answer_context/__init__.py` alongside the other builders.
- ✅ ensure maintenance extraction remains intact — `MaintenanceEntryMerger`/`KeyValueExtractor` wiring in `organize()` is untouched; `test_answer_context_organizer.py`'s existing maintenance-extraction tests pass unchanged, confirming the refactor is behavior-preserving.

**Design note on scope, found during implementation:** section 7's proposed tree also splits the *rest* of the package's existing files into `builders/`/`extractors/`/`mergers/`/`adapters/` physical subfolders (e.g. `answer_context_organizer.py` and `source_group_builder.py` moving under `builders/`, `key_value_extractor.py` under `extractors/`, `maintenance_entry_merger.py` under `mergers/`). That reorganization was deliberately not done in this phase — every file already involved is independently correct and independently tested; nesting them into subfolders is pure folder-churn with no functional driver and no violation it fixes, the same scoping discipline already applied in Phase 2 (which likewise deferred the full folder split in favor of moving only the data models that had a real reason to move). If a future phase needs the subfolder split (e.g. because the package grows past a size where flat files stop being navigable), it should be its own dedicated step, not bundled into "organizer redesign."

**Traceability correction:** the matrix row for 4.9 (`groups are prompt-facing only`) listed `Phase 5, Phase 7`. Re-checked 4.9's actual complaint: `AnswerSourceGroup`/`AnswerSectionGroup` are under-leveraged by renderers/CLI/research synthesis, not orchestration-only-ness of the organizer — that's a rendering-consumption concern (9.5, "unify deterministic rendering on top of the same typed context"), which is Phase 7's job. Phase 5 as scoped here does not touch grouping consumption at all, so the matrix below has been corrected to `Phase 7` only.

Verification: `ast.parse` on all three touched/created files, a runtime import check (`from ...answer_context import StructuredSourceBuilder, AnswerContextOrganizer`), the full existing `test_answer_context_organizer.py` suite (8 tests, all green, confirming behavior-preservation), a new `test_structured_source_builder.py` (6 tests covering sequential numbering, retrieval/chunk metadata mapping, collapsed-chunk-id defaulting, table-rows JSON decoding success/failure, and the chunk-type-name fallback), and a full `pytest tests/unit` run: **2243 passed, 0 failed, 0 errors.**

## Phase 6 - Format-Policy Upgrade and Diagnostic Consumption [IMPLEMENTED]

- ✅ remove the current fake resolve path — `resolve()`'s `_ = structured_context; return cls.for_intent(intent)` body was replaced with a real implementation that derives four context signals from `structured_context` and conditionally appends instruction lines driven by them.
- ✅ make `AnswerFormatPolicy.resolve()` context-aware (closes 9.4) — added `AnswerFormatPolicy._context_signals(structured_context)`, computing:
  - `is_sparse_evidence` (`source_count <= 1`) — 9.4's "evidence density" bullet.
  - `has_low_confidence_evidence` (any `AnswerKeyValue.confidence < 0.8`) — the concrete "low-confidence-evidence warning" 9.9 named as the example wiring target.
  - `has_rich_structured_evidence` (`structured_entities` non-empty, or any source has `table_rows`) — a single combined check standing in for 9.4's three separate "presence of typed entries / structured relationships / tables" bullets (see design note below).
  - `is_multi_document` (`len(diagnostics["document_ids"]) > 1`) — 9.4's "single-document vs mixed" bullet.
  Each signal, when true, appends one fixed instruction line to `instruction_lines` (which `AnswerPromptBuilder._format_policy_block()` already renders verbatim into the prompt — confirmed a live consumption path, not a second dead field). `AnswerFormatPolicy` gained an additive `context_signals: dict[str, bool] = field(default_factory=dict)` field so which signals fired is observable, not just baked silently into prompt text.
- ✅ consume the Phase 1 diagnostics baseline inside richer answer-format decisions — `is_multi_document` reads `structured_context.diagnostics["document_ids"]`, the exact diagnostic Phase 1/4 already populate on `AnswerContextOrganizer.organize()`.
- ✅ extend diagnostics only where the Phase 4/5 typed-view work introduces genuinely new signals — `has_rich_structured_evidence` is the only signal that reads a Phase 4/5 addition (`structured_entities`); the other three read pre-existing `StructuredAnswerContext` fields (`source_count`, `key_values`, `diagnostics`). `AnswerGenerationService._build_diagnostics()` now also surfaces `format_policy_context_signals` (the resolved policy's `context_signals` dict) alongside the existing `format_policy_rules_version`. `ANSWER_FORMAT_POLICY_RULES_VERSION` bumped `v1 -> v2` since `resolve()`'s behavior changed materially, matching the version's own stated purpose (correlate a future answer-quality regression against a specific policy-pack version) — its doc comment was updated to say so explicitly, since the original comment only mentioned `_POLICIES` table edits.
- ✅ add intent-plus-context policy tests — 13 new tests in `test_answer_format_policy.py` (one per signal firing/not-firing, a combined-signals test, a static-vs-resolved-with-no-context equivalence test, and a `caplog`-based structured-logging test mirroring `AnswerIntentAnalyzer`'s), plus one new diagnostics-wiring test in `test_answer_generation_service.py`.
- ✅ resolves 9.9's confidence-fields decision for `AnswerMaintenanceEntry.confidence`: traced its only producer (`KeyValueExtractor.extract_maintenance_entries`, hardcoded `confidence=0.88` on every single entry, with `MaintenanceEntryMerger`'s `max(left.confidence or 0.0, right.confidence or 0.0)` merge of two always-identical constants) and confirmed it has **zero possible variance** — every `AnswerMaintenanceEntry` ever constructed in this codebase carries exactly `0.88`, unlike `AnswerKeyValue.confidence` (see below). Removed the field entirely (`models/answer_maintenance_entry.py`, the `confidence=0.88` assignment, and both `confidence=...` merge-time lines in `maintenance_entry_merger.py`) rather than wiring a constant into the new low-confidence signal, which would have been decorative theater — a value that can never differ can never usefully warn about anything.
- ✅ resolves 9.9's confidence-fields decision for `AnswerKeyValue.confidence` the other way — traced its producers and found it is **not** uniformly decorative like the maintenance-entry field: `KeyValueExtractor` (chunk-text-derived key-values) hardcodes `0.9`, but `StructuredFactKeyValueBuilder` (resolved-entity/identifier-derived key-values, added in the Phase 4 era) propagates a real, variable `entity.get("confidence_score")` / `identifier.confidence_score` from the domain layer. Since a genuinely variable signal exists, kept the field and wired it into `has_low_confidence_evidence` above instead of removing it — the `0.8` threshold sits below both hardcoded deterministic-extraction baselines (`0.9`/former `0.88`) specifically so the signal only fires for real below-baseline domain confidence, not the constant baseline every chunk-text-derived key-value already carries.

**Design note on scope, found during implementation:** 9.4 lists "presence of tables", "presence of typed entries", and "presence of structured relationships" as three separate signals `resolve()` "should use". Implemented as one combined `has_rich_structured_evidence` check instead of three near-duplicate instruction lines, because all three point to the same underlying orchestration decision from the model's point of view ("richer evidence beyond flattened key-values exists — use its exact values instead of paraphrasing") — three separately-worded instructions saying essentially the same thing would bloat the prompt and dilute rather than sharpen the guidance, with no real behavioral difference between "an entity is present" and "a relationship on that entity is present" from the instruction's own wording. If a future need arises to react to *tables* specifically differently from *typed entities* specifically (e.g. a table-specific rendering hint), split the check apart then, driven by that concrete need rather than pre-emptively.

**Flagged, not touched:** while implementing this phase, found that `AnswerFormatPolicy.include_sources_inline` is itself a write-only field — every one of the 10 `_POLICIES` entries hardcodes it to `False`, and `AnswerPromptBuilder._format_policy_block()` never reads it (unlike `include_table`/`include_bullets`/`include_steps`/`max_bullets`/`preferred_format`/`response_label`/`instruction_lines`, which are all rendered into the prompt). This is the same shape of issue as 4.11, just not caught by the original audit since it isn't a "confidence" field. Deliberately not used as the delivery mechanism for the `is_multi_document` signal above (that would have been a second write-only use of an already-dead field, repeating the exact mistake 9.9 warns against) — the multi-document signal is expressed purely through `instruction_lines`, a confirmed-live path, instead. Wiring `include_sources_inline` up for real (having `AnswerPromptBuilder` actually change its citation rendering based on it) is a renderer-behavior change, not a format-policy-resolution change — that belongs in Phase 7 ("Renderer unification"), not here. Flagging for that phase rather than silently fixing or silently leaving inconsistent.

Full regression: 2256 tests green across the entire `tests/unit` suite (2243 before this phase + 13 new). New/changed tests: 13 new tests in `test_answer_format_policy.py`, 1 new test in `test_answer_generation_service.py` (`test_generate_diagnostics_surface_format_policy_context_signals`); no existing test assertions needed updating (the two pre-existing `resolve()` tests only assert `preferred_format`/`include_table`/`include_bullets`, none of which this phase's changes touch).

## Phase 7 - Renderer unification [IMPLEMENTED]

- ✅ refactor deterministic renderers to consume richer typed context (closes 4.7):
  - `SparePartsListRenderer.render()` now takes `sources: Sequence[AnswerSource]` (from `structured_context.sources`) instead of `chunks: Sequence[RetrievedChunk]`. `SparePartsTableParser.has_table_evidence()`/`section_title()`/`build_group()` now take `AnswerSource` too.
  - `IdentifierAnswerRenderer.render()` keeps the same signature, but the two loops inside it were reordered: `structured_context.key_values` (the typed model) is now processed *first* as the primary source, with the raw `resolved_identifiers: Sequence[Identifier]` processed *second*, only filling gaps not already covered (deduplicated via the existing `seen` fingerprint set). Previously it was the other way around — raw identifiers were primary and `structured_context` only filled gaps, which is backwards from "prefer the richer typed model" and is exactly what 4.7 flagged ("they operate on different input abstractions").
- ✅ remove duplicate ad-hoc parsing where context already provides the same information (closes part of 9.5) — `SparePartsTableParser._decode_table_rows(metadata)` was a second, independent JSON-decode of the exact same `table_rows_json` chunk metadata that `StructuredSourceBuilder._decode_table_rows()` (Phase 5) already decodes once into `AnswerSource.table_rows`. `_rows_from_structured_grid()` now takes the pre-decoded `grid: list[list[str]] | None` directly; the parser's own `_decode_table_rows()` and its `import json` were deleted entirely.

**Design note on scope, found during implementation:** traced whether `IdentifierAnswerRenderer`'s raw `resolved_identifiers` path could be removed outright now that `structured_context.key_values` is primary (which would have been a cleaner, fuller unification). Found it can't: `QuestionAnsweringWorkflow._join_structured_facts()` only converts an identifier into an `AnswerKeyValue` if its source chunk's `source_number` is resolvable, which requires `_document_lookup_service` to be configured to fetch chunks not already in the retrieval set. When no lookup service is configured, an identifier never reaches `key_values` at all — the exact same degraded-mode gap Phase 4 already accepted as intentional for `structured_entities` (see `test_resolved_structured_entities_without_lookup_service_do_not_crash`). Keeping the raw fallback preserves that resilience; removing it would silently drop identifiers in the degraded case instead of just losing their typed representation. Documented and tested (`test_render_falls_back_to_raw_identifiers_when_structured_context_is_none`) rather than silently kept as an unexplained duplicate path.

**Not addressed, left open with reasoning:** 4.9 (`AnswerSourceGroup`/`AnswerSectionGroup` under-leveraged by deterministic renderers) is mapped to this phase in the traceability matrix. Investigated whether `SparePartsListRenderer` should pull from `structured_context.source_groups` (grouped by `chunk_type`, which already exactly matches its own `chunk_type == "spare_parts_table"` filter) instead of filtering `sources` directly. Decided against it: both are the identical single O(n) filter/lookup over the same underlying list — routing through `AnswerSourceGroup` instead of a direct filter is not a real simplification or duplicate-parsing removal, just a cosmetic reshuffle for the sake of "using the model," which would have meant re-churning the same test file's fixtures a second time in one phase for no functional gain. 4.9 remains open; it needs a renderer or presentation layer that genuinely benefits from per-section/per-chunk-type grouping (e.g. a future CLI or research-style structured presentation, per 4.9's own "not yet reusable by... CLI presentation, or research-style structured synthesis" framing) to be a real fix rather than busy-work.
- 4.17 (`AnswerFormatPolicy.include_sources_inline`, flagged in Phase 6) also remains open for the same reason: wiring it up means building a wholly new "inline citation" rendering capability that doesn't exist anywhere today, not consolidating an existing dual-representation — out of scope for a renderer-*unification* phase.

Full regression: run alongside Phase 6's changes; see Phase 6 and this phase's own test additions (`test_spare_parts_list_renderer.py` fixture rebuilt on `AnswerSource` via the real `StructuredSourceBuilder` — no manual mapping duplicated in the test — all 27 pre-existing tests pass unchanged; `test_identifier_answer_renderer.py` gained 2 new tests locking in the new preference order and the degraded-mode fallback, all 19 tests green).

## Phase 8 - Prompt/schema hardening [IMPLEMENTED]

- ✅ upgrade prompt builder to serialize the richer context cleanly (closes 4.5's `structured_entities` gap) — found, while auditing `AnswerPromptBuilder._organized_context_block()`, that `StructuredAnswerContext.structured_entities` (Phase 4's typed evidence view, with `.relationships[*].target_entity_fields`) was **never serialized into the LLM prompt at all** — only the flattened `key_values` were. This meant the 4.16 fix (a resolved `task_uses_procedure` relationship's `steps` surviving onto `AnswerRelationship.target_entity_fields["steps"]`) only ever reached the two deterministic renderers, never the LLM-generation path itself — the exact same "resolved data silently never reaches the answer" shape as 4.3/4.16, one hop further down, specific to the LLM path. Added a "Structured entities:" block to `_organized_context_block()` that renders each entity's `entity_type`/`entity_id`/`fields`, plus each of its `relationships` (`relationship_type -> target_entity_type [target_entity_id]: target_entity_fields`), with list-valued fields (e.g. `steps`) joined with `"; "`. Some overlap with the existing `key_values` block is expected and accepted, matching 4.2's own established precedent ("AnswerKeyValue extraction still runs in parallel unchanged... this is additive, not a replacement") — the new block's real value is the fields `StructuredFactKeyValueBuilder` has no label-map entry for (steps being the concrete case), not deduplication against `key_values`.
- ✅ strengthen the pydantic response schema for answer generation (partial implementation of 9.6, see design note) — added an optional `limitation_note: str | None` field to `AnswerGenerationResponsePayload`, threaded through unchanged (`extra="forbid"` still enforced) to a new `GeneratedAnswer.limitation_note` field, so a caller can check "did the model flag an explicit limitation" as a real typed field instead of string-parsing `answer_text`. `AnswerPromptBuilder.build()`'s JSON-shape instructions updated to describe the new optional field to the model.
- ✅ keep parser strict — no change needed to `AnswerGenerationResponseParser`; pydantic validation (and `extra="forbid"`) already rejects anything not declared on the schema, and adding a new *declared* optional field doesn't loosen that.

**Design note on scope, found during implementation:** 9.6 proposes evolving the schema toward `answer_text` + `limitation_note` + `sections` + `reference_notes`. Implemented `limitation_note` only, not `sections`/`reference_notes`. Reason: traced every consumer of `GeneratedAnswer.answer_text` (`answer_support_guardrail.py`, `citation_guardrail.py`, `safety_answer_guardrail.py`, `unsupported_claim_guardrail.py`, `unsupported_suggestion_guardrail.py`, `answer_question_tool.py`, `question_answering_workflow.py`) and found every single one of them is built around one flat answer string. Adding `sections`/`reference_notes` today would either (a) sit as unconsumed fields — repeating the exact 4.11/4.17 "decorative field with no reader" mistake this plan has now caught three times — or (b) require redesigning how every guardrail scans an answer for claims/citations to work over structured sections instead of prose, which is a genuinely different, much larger piece of work than "hardening" the existing schema. `limitation_note` was implemented because it has a real, immediate, non-decorative consumer (`GeneratedAnswer.limitation_note` itself, a first-class typed field any caller can branch on today) without needing that redesign. `sections`/`reference_notes` are left as explicit future work, gated on a guardrail-layer redesign that is out of this phase's scope.

Full regression: 2261 tests green across the entire `tests/unit` suite (2258 before this phase + 3 new). New tests: `test_answer_prompt_builder_serializes_structured_entities_and_relationships`, `test_answer_prompt_builder_omits_structured_entities_block_when_absent` (`test_answer_prompt_builder.py`), `test_generate_surfaces_limitation_note_from_llm_response` (`test_answer_generation_service.py`); `test_generate_returns_llm_output_as_answer_text` extended to assert `limitation_note is None` for a response that omits it.

## Phase 9 - Cleanup / dead code removal [IMPLEMENTED]

- ✅ remove replaced prompt-only helpers — audited `AnswerPromptBuilder` and found `_raw_source_block()`'s `RetrievedChunk`-based fallback branch (plus its two sole helpers, `_format_source_block()` and `_format_page_range()`) was dead in production: the one real caller (`AnswerGenerationService.generate()`) always calls `build()` with a `resolved_request` from `_resolve_request()`, which unconditionally organizes `structured_context` before `build()` ever runs — so the `AnswerSource`-based path is always taken, and the `RetrievedChunk` fallback (added originally for a caller that predates `structured_context` always being populated) was unreachable with real data. Removed both helpers, the now-unused `RetrievedChunk` import, and simplified `_raw_source_block()` to return `""` when `structured_context` is `None`/empty instead of re-deriving a source block from raw chunks. Removed the one test (`test_answer_prompt_builder_formats_page_ranges`) that only existed to exercise the now-deleted `_format_page_range()`, replaced with a test locking in the new explicit empty-block behavior.
- ✅ remove write-only confidence fields unless a calibrated consumer has been deliberately introduced — already fully resolved in Phase 6 (4.11/9.9); nothing further found this phase.
- ✅ remove obsolete flattening logic / remove no-longer-used projections — swept `answer_generation`/`answer_context` with `ruff --select F401,F841` (zero findings — no unused imports/locals anywhere in scope) plus manual review, which surfaced two further dead-field findings beyond what Phases 6–7 had already caught:
  - closed 4.17 (`AnswerFormatPolicy.include_sources_inline`, flagged in Phase 6, deferred in Phase 7 as feature work) — since no phase in this plan intends to build the "inline citations" feature it was reserved for, removed the field outright rather than leaving it dead indefinitely. Deleted from the dataclass and all 10 `_POLICIES` entries.
  - found and closed 4.18 (new): `AnswerGenerationRequest.document_id` and `.require_citations` were set at their one production construction site and never read anywhere downstream. `require_citations` in particular was a dead duplicate of a concept the citation guardrail already implements via its own, unrelated config. Removed both fields and their assignment at the single call site in `question_answering_workflow.py`.
  - evaluated all three items in 5.2 ("removal candidates after replacement exists") — none had actually materialized (see 5.2's own updated status); nothing to remove there.
- ✅ update `__init__.py` exports — audited `answer_context/__init__.py` and `services/answer_generation/__init__.py`; both already complete and consistent (every public class from Phases 2–8 already exported via the lazy `__getattr__` pattern), no changes needed.

Full regression: 2261 tests green across the entire `tests/unit` suite (same count as end of Phase 8 — one dead test removed, one new test added, net zero). `ruff check --select F401,F841` clean across the full `answer_context`/`answer_generation` subtree both before and after this phase's removals.

## Phase 10 - Full validation [IMPLEMENTED]

- ✅ targeted unit tests first — already the standing practice throughout every phase (each phase ran its directly-affected test file(s) before the full suite); nothing further needed here beyond confirming that discipline held, which the full-suite result below confirms.
- ✅ then question-answering, prompt, and langgraph integration tests touching this path — ran `tests/unit/application/workflows/question_answering/`, `tests/unit/application/prompts/`, `tests/unit/application/langgraph/`, and `tests/unit/application/services/answer_generation/` together: 546 passed, 0 failed, 0 errors. (This codebase has no separate `tests/integration` suite for this path — `tests/integration/` is exclusively DB-repository tests; the "integration tests" this bullet means are the broader unit-level tests in the directories above, which already exercise multiple components wired together via fakes, e.g. `test_question_answering_workflow.py`.)

**Found and fixed during validation:** re-read section 9.6's "does not mean exposing raw internal ids" caution while auditing Phase 8's new prompt content, and checked whether it was actually honored. `ANSWER_GROUNDING_RULES` already explicitly told the model not to reference "SOURCE labels, source numbers, chunk IDs, section IDs, or internal metadata" — but Phase 8's new "Structured entities:" prompt block serializes `entity_id`/`target_entity_id` values (raw domain identifiers, e.g. `task_001`) as grounding context, and neither "entity IDs" nor "relationship types" were named in that instruction the way chunk/section IDs already explicitly were. The generic "internal metadata" catch-all may or may not have been enough on its own; rather than leave it to chance, extended the instruction to name entity/relationship ids explicitly, matching the existing convention of naming each category rather than relying only on a catch-all. Added `test_answer_prompt_builder_instructs_against_leaking_entity_ids` to lock this in.

**Section 11 checklist audit** (below): every "New tests to add" bullet and every "Existing tests to update" area was checked against the actual test suite and confirmed to have real, current coverage — cross-references added inline in section 11 below rather than repeated here.

Final full regression: **2262 tests green** across the entire `tests/unit` suite (2261 before this phase + 1 new grounding-rules test), 0 failed, 0 errors. `ruff check --select F401,F841,F811` clean across `answer_context`, `answer_generation`, `prompts/answer_generation`, and `prompts/common`. This closes the plan: all 10 phases are now `[IMPLEMENTED]` or `[PARTIALLY IMPLEMENTED]` with an explicit, documented reason for every deferral.

## 11. Test Plan For Implementation [AUDITED in Phase 10 -- all items confirmed covered]

### New tests to add

- `AnswerSource` preserves retrieval metadata, split-family metadata, and asset/table metadata — ✅ `test_answer_context_organizer.py::test_context_organizer_enriches_source_with_retrieval_metadata`, `::test_context_organizer_normalizes_collapsed_chunk_ids_from_csv_metadata`, `::test_context_organizer_defaults_collapsed_chunk_ids_when_not_deduplicated`; `test_structured_source_builder.py` (Phase 5)
- structured relationships survive into `StructuredAnswerContext` — ✅ `test_structured_evidence_view_builder.py`; `test_question_answering_workflow.py::test_resolved_maintenance_task_surfaces_linked_procedure_steps_end_to_end`
- context is retained even when no extra key-values are produced — ✅ `test_question_answering_workflow.py::test_resolved_structured_entities_without_lookup_service_do_not_crash` (corrected in Phase 4 for the 4.3/9.7 fix)
- `AnswerFormatPolicy.resolve()` changes behavior based on real context — ✅ 13 tests in `test_answer_format_policy.py` (Phase 6)
- deterministic renderers consume typed context instead of reparsing raw text where possible — ✅ `test_spare_parts_list_renderer.py` (rebuilt on `AnswerSource`), `test_identifier_answer_renderer.py` (typed-context-first preference order) (Phase 7)
- prompt builder emits richer organized context without leaking internal ids — ✅ `test_answer_prompt_builder_serializes_structured_entities_and_relationships` (Phase 8); `test_answer_prompt_builder_instructs_against_leaking_entity_ids` (Phase 10, closing the "without leaking internal ids" half of this bullet specifically)
- answer-generation schema rejects malformed structured output cleanly — ✅ `test_answer_generation_service.py::test_generate_rejects_malformed_answer_generation_json`
- every `AnswerIntent` member has a corresponding `AnswerFormatPolicy._POLICIES` entry (added in this amendment — see 9.8) — ✅ `test_answer_format_policy.py::test_every_answer_intent_has_a_dedicated_format_policy_entry` (Phase 1)
- `AnswerGenerationService` does not recompute `AnswerIntentAnalyzer.analyze()` when `AnswerGenerationRequest.answer_intent_decision` is already set, and still computes it when absent (added in this amendment - regression coverage for section 0.1 already exists in `tests/unit/application/services/answer_generation/test_answer_generation_service.py` and `tests/unit/application/workflows/question_answering/test_question_answering_workflow.py::test_answer_intent_is_resolved_exactly_once_when_structured_facts_are_joined`; keep these passing through the refactor) — ✅ confirmed still green through every subsequent phase

### Existing tests to update

- organizer tests — ✅ `test_answer_context_organizer.py` updated across Phases 1-5
- format policy tests — ✅ `test_answer_format_policy.py` updated Phase 1 (9.8 guard) and Phase 6 (context-aware `resolve()`)
- answer generation service tests — ✅ `test_answer_generation_service.py` updated Phases 4, 6, 8, 9
- prompt builder tests — ✅ `test_answer_prompt_builder.py` updated Phases 8, 9, 10
- workflow tests that assert current structured-context behavior — ✅ `test_question_answering_workflow.py` updated Phase 4

## 12. Decisions

These were open review questions in the original audit. None were contested, so each is adopted here using this document's own stated recommendation, and the numbered phases above are written against these answers. Revisit before starting the phase noted if the team's priorities change.

1. Should `StructuredAnswerContext` remain the single canonical answer-context DTO for both deterministic renderers and LLM prompting?
   - **Decision: Yes.** Phases 4, 5, and 7 are written on this basis - renderer unification (Phase 7) only makes sense if there is one shared DTO to unify on.

2. Should we keep `AnswerKeyValue` as a secondary convenience view rather than the main structured-evidence view?
   - **Decision: Yes.** Phase 4 explicitly keeps it as a convenience projection alongside the new typed views, not a replacement for them.

3. Should deterministic answer rendering expand beyond identifiers and spare parts once typed structured views exist?
   - **Decision: Yes, phased after the context refactor.** This is why Phase 7 (renderer unification) is sequenced after Phase 4 (typed views), not before.

4. Should prompt/output schema strengthening happen in the same implementation wave or after context refactor stabilization?
   - **Decision: Same wave, after context refactor and before cleanup.** This is why Phase 8 (prompt/schema hardening) is sequenced after Phases 4-7 and before Phase 9 (cleanup).

## 13. Risk, Rollback, and Compatibility Strategy

- **Backward compatibility:** no *temporary* compatibility shims - no duplicate old/new module paths, no parallel file trees kept alive during migration, no re-export bridges added solely to avoid updating call sites. Every import site of a moved/renamed symbol is updated in the same change as the move, matching this codebase's established direct-cutover convention. This does **not** forbid the package's own stable `__init__.py` export surface (section 7's proposed structure keeps `answer_context/__init__.py` as the one import path consumers use) - that is the package's permanent public interface, not a migration-era compatibility shim, and Phase 2 is expected to preserve it.
- **Rollback unit:** each phase is scoped to be independently revertible - Phase 2's file split lands before Phase 3-8 add new behavior on top of it, so a problem discovered in, say, Phase 6 can be reverted without unwinding Phases 2-5. Do not squash multiple phases into one change; that is what makes the phase boundaries in section 10 meaningful.
- **Sequencing constraint:** Phases 3 through 8 assume Phase 2's model split has already landed (they add fields/types to files that Phase 2 relocates). Do not start Phase 4 before Phase 2 merges.
- **Blast radius:** contained to the question-answering and structured-retrieval answer-generation path (`answer_context/`, `answer_generation/`, `prompts/answer_generation/`, and the structured query-analysis files added to scope in 2.1). Ingestion, extraction, and other LangGraph nodes outside answer generation are not touched by this plan.
- **Test gate per phase:** each phase's exit criteria (where stated inline) and the traceability matrix (10.0) together define "done" for that phase - a phase is not complete until its mapped issue's `### Impact` bullets in section 4 no longer apply and its existing test suite (section 8.3) is green.

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

The package-structure proposal is good, but the earlier tree block contained mojibake box-drawing characters (`|--` rendered incorrectly in some viewers, along with other box-drawing glyphs).

That is only a documentation readability issue, not an architecture issue, but it should be cleaned before implementation starts so the structure can be copied safely.

## 13.2 Resolution Of Reviewer Comments

All five comments above are addressed as of this pass:

1. **Compatibility wording clarified.** Section 13's backward-compatibility bullet now explicitly distinguishes "no temporary migration-era shims/parallel trees" from "the package's own stable `__init__.py` export surface, which Phase 2 is expected to preserve." No conflict with section 7/Phase 2 remains.
2. **4.3/9.7 urgency elevated.** Phase 4 now states it is the first change in that phase, ahead of the typed-view work, and explicitly calls out that it can be pulled forward as a standalone micro-fix before Phase 2/3 if the team wants risk reduction sooner - it needs no new types, only removing the dead-path check. The traceability matrix (10.0) still shows it mapped to Phase 4 since that is where it will land by default; treat the micro-fix option as team discretion, not a doc inconsistency.
3. **Phase 2 behavior-preservation made explicit.** Added the three consumers that must move together (`MaintenanceEntryMerger`, `MaintenancePromptContextFormatter`, `AnswerContextOrganizer`), named the existing tests that must stay green with no assertion changes (`test_maintenance_entry_merger.py`, the maintenance-path tests in `test_answer_generation_service.py`), and explicitly deferred any answer-shape improvement to Phase 4+.
4. **Observability-ordering corrected in the plan.** Baseline rules-version and diagnostics work now lands in Phase 1 so the refactor is measurable from the start; Phase 6 now consumes and extends that baseline instead of introducing it late.
5. **Tree snippet normalized to ASCII** (`|--`, `` `-- ``, `|` instead of Unicode box-drawing). Note for the record: the file's on-disk bytes were checked and were valid UTF-8 box-drawing characters, not actually corrupted - the mojibake was a rendering artifact in whatever viewer displayed it garbled. Normalizing to ASCII removes that fragility regardless of cause, since it renders identically in any editor/terminal/encoding.

## 14. Final Recommendation

The right upgrade path is not to patch the prompt builder again.

The right path is:

- enrich the answer-context model — ✅ done (Phases 2-3)
- preserve structured semantics — ✅ done (Phase 4)
- make format policy context-aware — ✅ done (Phase 6)
- unify deterministic and LLM answer generation on the same typed context — ✅ done (Phases 7-8)
- then remove the dead and low-value code that becomes unnecessary — ✅ done (Phase 9), validated (Phase 10)

That will move this area from "helpful prompt helper" to "enterprise answer-evidence layer".

**Outcome:** all 10 phases implemented per this recommendation's own ordering. `StructuredAnswerContext` is now the canonical answer-evidence projection consumed by the organizer, both deterministic renderers, the format policy, and the LLM prompt builder alike — the single-shared-DTO goal from Decision #1 (section 12) is realized in practice, not just decided on paper. Two items remain open by explicit, documented design choice rather than left incomplete: 4.8 (table evidence) and 4.9 (source/section groups) — both re-evaluated as recently as Phase 9 and found to have no concrete, non-speculative next step yet. `sections`/`reference_notes` (9.6) are the one clearly-scoped piece of future work, gated on a guardrail-layer redesign that is deliberately out of this plan's scope.

