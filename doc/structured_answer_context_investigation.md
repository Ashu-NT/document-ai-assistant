# StructuredAnswerContext Investigation Report

## Executive Conclusion

`StructuredAnswerContext` is not just a flat string container.

The current pipeline does preserve structured evidence in application memory through typed models such as:

- `AnswerSource`
- `AnswerKeyValue`
- `AnswerMaintenanceEntry`
- `AnswerStructuredEntity`
- `AnswerRelationship`
- `AnswerSourceGroup`
- `AnswerSectionGroup`

That structure is assembled before answer generation and is used directly by some deterministic answer renderers.

However, for the generic LLM answer path, the structure is ultimately serialized into prompt text by `AnswerPromptBuilder`. That means the system is:

- structured in memory
- semi-structured at the prompt boundary
- not fully machine-structured inside the LLM context window

So the short answer is:

- it does maintain structured evidence internally
- it does flatten that structure into text before sending it to the LLM

This is better than raw chunk dumping, but it is not the same as giving the model a fully structured JSON/XML evidence object.

## Main Files Involved

### Context assembly

- `src/application/workflows/question_answering/answer_context/answer_context_organizer.py`
- `src/application/workflows/question_answering/answer_context/structured_source_builder.py`
- `src/application/workflows/question_answering/answer_context/key_value_extractor.py`
- `src/application/workflows/question_answering/answer_context/source_group_builder.py`
- `src/application/workflows/question_answering/answer_context/section_group_builder.py`
- `src/application/workflows/question_answering/answer_context/structured_fact_key_value_builder.py`
- `src/application/workflows/question_answering/answer_context/structured_evidence_view_builder.py`

### Context models

- `src/application/workflows/question_answering/answer_context/models/structured_answer_context.py`
- `src/application/workflows/question_answering/answer_context/models/answer_source.py`
- `src/application/workflows/question_answering/answer_context/models/answer_key_value.py`
- `src/application/workflows/question_answering/answer_context/models/answer_maintenance_entry.py`
- `src/application/workflows/question_answering/answer_context/models/answer_structured_entity.py`
- `src/application/workflows/question_answering/answer_context/models/answer_relationship.py`
- `src/application/workflows/question_answering/answer_context/models/answer_groups.py`

### Upstream enrichment

- `src/application/workflows/question_answering/question_answering_workflow.py`
- `src/application/workflows/question_answering/evidence/final_evidence_preparer.py`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/retrieval/structured/structured_evidence_resolver.py`

### Downstream answer generation

- `src/application/services/answer_generation/answer_generation_service.py`
- `src/application/services/answer_generation/answer_generation_request.py`
- `src/application/prompts/answer_generation/answer_prompt_builder.py`
- `src/application/prompts/answer_generation/maintenance_prompt_context_formatter.py`

### Direct structured-data consumers

- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py`
- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py`
- `src/application/services/answer_generation/formatting/answer_format_policy.py`

## End-to-End Flow

## 1. Retrieved evidence is first upgraded before context organization

The answer path does not build `StructuredAnswerContext` directly from raw retrieval output only.

In `QuestionAnsweringWorkflow._join_structured_facts()`:

- approved retrieval chunks are taken as the base set
- extra source chunks are fetched for resolved identifiers and resolved structured entities if those chunks were not already retrieved
- `FinalEvidencePreparer.prepare()` is called before context organization

Relevant code:

- `src/application/workflows/question_answering/question_answering_workflow.py:442-547`
- `src/application/workflows/question_answering/evidence/final_evidence_preparer.py:26-46`

`FinalEvidencePreparer` does two important things:

1. table hydration
2. retrieval deduplication

So `StructuredAnswerContext` is built from post-processed evidence, not the initial raw chunk list.

## 2. Table evidence is partially restructured before context building

`TableEvidenceHydrator.hydrate()` loads the original `DocumentGraph`, finds table assets linked to retrieved chunks, and can replace chunk content with richer table text:

- `TableAsset.to_embedding_text()`
- `TableAsset.to_structured_row_text()`

It also injects:

- `metadata["table_evidence_hydrated"] = "true"`
- `metadata["table_rows_json"] = json.dumps(structured_table.rows)`

Relevant code:

- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py:19-90`

This matters because table structure is not lost immediately. It survives at least into chunk metadata and then into `AnswerSource.table_rows`.

## 3. Structured retrieval evidence is also merged in

`StructuredEvidenceResolver` returns:

- identifiers
- structured entity dicts
- extra chunks associated with those facts

Relevant code:

- `src/application/workflows/retrieval/structured/structured_evidence_bundle.py:10-18`
- `src/application/workflows/retrieval/structured/structured_evidence_resolver.py:36-65`

Those structured entity dicts can include:

- `_entity_type`
- entity fields
- `source_chunk_id`
- `related_entities`

So the pipeline does have a genuine structured evidence layer before answer generation.

## 4. `AnswerContextOrganizer` builds the main structured context object

`AnswerContextOrganizer.organize()` is the orchestration point.

Relevant code:

- `src/application/workflows/question_answering/answer_context/answer_context_organizer.py:30-104`

It builds:

1. `sources` via `StructuredSourceBuilder.build_sources()`
2. `source_groups` via `SourceGroupBuilder.build()`
3. `section_groups` via `SectionGroupBuilder.build()`
4. `key_values` via `KeyValueExtractor.extract()`
5. `maintenance_entries` via `KeyValueExtractor.extract_maintenance_entries()`
6. merged maintenance entries via `MaintenanceEntryMerger.merge()`
7. diagnostics

Then it returns a `StructuredAnswerContext`.

This is a real structured object graph, not a prompt string.

## What Exactly Is Preserved Structurally

## 1. Source-level structure is preserved

`StructuredSourceBuilder` maps each `RetrievedChunk` into `AnswerSource`.

Relevant code:

- `src/application/workflows/question_answering/answer_context/structured_source_builder.py:12-78`
- `src/application/workflows/question_answering/answer_context/models/answer_source.py:10-43`

Each `AnswerSource` keeps:

- `source_number`
- `chunk_id`
- `chunk_name`
- `chunk_type`
- `document_id`
- `document_title`
- `section_path`
- `page_start`
- `page_end`
- `score`
- `content`
- `table_rows`
- `retrieval_source`
- `section_id`
- `statistics`
- `identifier_values`
- `metadata`
- `collapsed_chunk_ids`

Important finding:

`table_rows_json` is decoded into `AnswerSource.table_rows`.

So table structure is still available in typed form at this stage.

## 2. Key-value facts are preserved as typed objects

`KeyValueExtractor.extract()` builds `AnswerKeyValue` objects from:

- chunk text lines
- markdown-style table rows found in chunk text
- explicit `AnswerSource.table_rows`

Relevant code:

- `src/application/workflows/question_answering/answer_context/key_value_extractor.py:137-175`
- `src/application/workflows/question_answering/answer_context/key_value_extractor.py:224-262`
- `src/application/workflows/question_answering/answer_context/models/answer_key_value.py:6-12`

This means a technical specification table can become typed key/value facts before answer generation.

## 3. Maintenance evidence is preserved more richly than generic key-values

For `AnswerIntent.MAINTENANCE_SUMMARY`, the same extractor builds `AnswerMaintenanceEntry` objects.

Relevant code:

- `src/application/workflows/question_answering/answer_context/key_value_extractor.py:177-222`
- `src/application/workflows/question_answering/answer_context/key_value_extractor.py:264-536`
- `src/application/workflows/question_answering/answer_context/models/answer_maintenance_entry.py:6-68`

Each maintenance entry preserves:

- task
- interval
- component
- notes
- description
- references

Each reference preserves:

- source number
- page start/end
- section path

This is substantially more structured than plain chunk flattening.

## 4. Structured entities and relationships are preserved

`StructuredEvidenceViewBuilder` converts raw resolved entity dicts into:

- `AnswerStructuredEntity`
- `AnswerRelationship`

Relevant code:

- `src/application/workflows/question_answering/answer_context/structured_evidence_view_builder.py:30-146`
- `src/application/workflows/question_answering/answer_context/models/answer_structured_entity.py:10-26`
- `src/application/workflows/question_answering/answer_context/models/answer_relationship.py:6-19`

This preserves:

- entity type
- entity id
- entity fields
- source chunk id
- typed relationships to related entities
- related entity fields

This is one of the strongest parts of the current design.

## 5. Grouping structure is preserved

Two additional views are created:

- `AnswerSourceGroup` grouped by chunk type
- `AnswerSectionGroup` grouped by section path

Relevant code:

- `src/application/workflows/question_answering/answer_context/source_group_builder.py:12-27`
- `src/application/workflows/question_answering/answer_context/section_group_builder.py:12-50`
- `src/application/workflows/question_answering/answer_context/models/answer_groups.py:10-23`

These are useful summary structures, but they are relatively shallow and mostly organizational.

## Where Additional Flattening Starts Before Prompting

## 1. Structured entities are duplicated into flat key-values

`QuestionAnsweringWorkflow._join_structured_facts()` does not only preserve structured entities.

It also projects them into `AnswerKeyValue` objects through `StructuredFactKeyValueBuilder`.

Relevant code:

- `src/application/workflows/question_answering/question_answering_workflow.py:499-547`
- `src/application/workflows/question_answering/answer_context/structured_fact_key_value_builder.py:42-158`

This means the same fact can exist in two forms:

- rich structured entity form
- flattened key/value form

That is useful for answer rendering and prompting, but it is also the first clear place where structured evidence is intentionally simplified.

## 2. `StructuredAnswerContext` is the last strongly typed boundary

`StructuredAnswerContext` itself remains typed:

- `sources`
- `source_groups`
- `section_groups`
- `key_values`
- `maintenance_entries`
- `structured_entities`
- `diagnostics`

Relevant code:

- `src/application/workflows/question_answering/answer_context/models/structured_answer_context.py:27-44`

This is the final in-memory structured representation before prompt construction.

## Exact Flattening Boundary for the LLM Path

## 1. `AnswerGenerationService` still carries the typed object

`AnswerGenerationService.generate()` receives `AnswerGenerationRequest`, and that request can contain `structured_context`.

Relevant code:

- `src/application/services/answer_generation/answer_generation_request.py:20-43`
- `src/application/services/answer_generation/answer_generation_service.py:92-173`
- `src/application/services/answer_generation/answer_generation_service.py:187-221`

If `structured_context` is missing, `AnswerGenerationService` can build it itself.

So up to this point, the answer layer still has full structured access.

## 2. Deterministic renderers use structured data directly

Before calling the LLM, `AnswerGenerationService` gives deterministic renderers a chance to answer.

Relevant code:

- `src/application/services/answer_generation/answer_generation_service.py:112-151`
- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py:64-143`
- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py:55-207`

Important finding:

These renderers do consume structure directly.

Examples:

- `IdentifierAnswerRenderer` reads `structured_context.key_values`
- `SparePartsListRenderer` reads `AnswerSource.table_rows` and structured spare-part entities

So for deterministic answers, the system does not flatten first.

## 3. The generic LLM path serializes everything into prompt text

If no deterministic renderer answers, `AnswerGenerationService` calls:

- `prompt = self.prompt_builder.build(resolved_request)`

Relevant code:

- `src/application/services/answer_generation/answer_generation_service.py:153-173`
- `src/application/prompts/answer_generation/answer_prompt_builder.py:38-56`

This is the true flattening boundary for generic answer generation.

## How the LLM actually sees the context

`AnswerPromptBuilder` creates two major evidence sections:

1. `Organized context:`
2. `Raw sources:`

Relevant code:

- `src/application/prompts/answer_generation/answer_prompt_builder.py:104-161`
- `src/application/prompts/answer_generation/answer_prompt_builder.py:174-198`

### Organized context

This block contains:

- answer intent
- source count
- formatted maintenance entries
- flat key-values
- structured entities rendered as lines
- relationship lines
- source group summaries
- section group summaries

But this is all serialized into plain text lines.

Examples of the serialization style:

- `- [SOURCE 2] Pressure: 10 bar`
- `- manufacturer [man_1]: name: X, website: Y`
- `  - supplies -> spare_part [sp_1]: part_number: Z, description: ...`

This is organized, but it is not a nested machine-readable object anymore.

### Raw sources

This block then appends each source as text:

- source number
- document title
- section path
- pages
- raw content

So the LLM still gets the original chunk text after the organized summary block.

## Does the current design preserve structure for the LLM?

### Yes, partially

The LLM does receive evidence that is better structured than raw chunk dumping:

- maintenance entries are formatted as consistent blocks
- key-values are normalized
- entity relationships are explicitly named
- source numbers and provenance remain visible
- raw sources are still included for grounding

### But no, not in a fully structured sense

The LLM does not receive:

- nested JSON for `StructuredAnswerContext`
- explicit structured row arrays as arrays
- entity/relationship objects in machine-readable form
- a source-to-entity mapping schema beyond textual labels

Instead, the LLM receives a text rendering of those objects.

So the design is:

- semantically enriched
- prompt-organized
- not schema-structured at inference time

## Specific Observations About Flattening Quality

## 1. `structured_entities` are preserved better than before, but still stringified

`AnswerPromptBuilder._organized_context_block()` loops over `structured_entities` and calls `_format_entity_fields()`.

Relevant code:

- `src/application/prompts/answer_generation/answer_prompt_builder.py:127-172`

That helper converts entity fields into comma-joined strings:

- lists become `"; "`-joined text
- fields become `"key: value"` pairs
- relationships become textual child lines

This keeps semantics visible, but complex entity structure is flattened into prose-like strings.

## 2. Table structure is only partially carried into the prompt

`AnswerSource.table_rows` exists and is used by:

- `KeyValueExtractor`
- `SparePartsListRenderer`
- `AnswerFormatPolicy`

Relevant code:

- `src/application/workflows/question_answering/answer_context/structured_source_builder.py:49-78`
- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py:66-70`
- `src/application/services/answer_generation/formatting/answer_format_policy.py:122-129`

But in the generic LLM prompt path:

- there is no dedicated row-grid rendering block
- table rows are only reflected indirectly through extracted key-values, maintenance entries, or hydrated raw text

So the model does not receive table structure as an explicit table object.

## 3. Section and grouping structure is shallow

`SourceGroupBuilder` groups only by `chunk_type`.

`SectionGroupBuilder` groups only by the final `section_path` string.

Relevant code:

- `src/application/workflows/question_answering/answer_context/source_group_builder.py:12-27`
- `src/application/workflows/question_answering/answer_context/section_group_builder.py:12-50`

This is useful for organization, but it is not a deep semantic hierarchy.

## 4. The raw source block can dominate the context window

The prompt includes both:

- organized evidence summaries
- full raw source text blocks

Relevant code:

- `src/application/prompts/answer_generation/answer_prompt_builder.py:41-56`
- `src/application/prompts/answer_generation/answer_prompt_builder.py:174-198`

For the LLM, this means the carefully structured layer competes with a larger flat text layer later in the same prompt.

That weakens the practical benefit of the structured layer, especially when many sources are present.

## Strengths of the Current Design

## 1. Strong internal structure before prompting

The application layer genuinely models:

- source provenance
- normalized facts
- maintenance-specific records
- typed entities
- entity relationships
- grouping summaries

This is a strong enterprise direction.

## 2. Structured evidence is not thrown away immediately

Table rows and resolved structured entities survive long enough to influence:

- answer intent formatting policy
- deterministic answer rendering
- organized prompt context

## 3. Deterministic answerers already prove the structure is useful

The deterministic renderers are the clearest proof that the structured layer has real value.

They use typed context directly instead of re-parsing flat prompt text.

## Weaknesses / Gaps

## 1. The generic LLM still gets text, not true structured context

This is the central issue.

`StructuredAnswerContext` is structured in Python, but not preserved as structured data at the prompt boundary.

## 2. There are parallel representations of the same evidence

The same information can appear as:

- raw source content
- table rows
- `AnswerKeyValue`
- `AnswerMaintenanceEntry`
- `AnswerStructuredEntity`
- relationship lines

This improves recall, but it also increases duplication and prompt noise.

## 3. Relationship semantics are reduced to text lines

`AnswerRelationship` is rich in memory, but by prompt time it becomes:

- relationship label
- target entity type/id
- flattened field string

That is readable, but less precise than a structured graph serialization.

## 4. Table semantics are underexposed to the generic LLM

The system does hydrate table evidence and preserve row grids, but the generic prompt path does not surface those row grids as a first-class structured section.

## 5. Source groups and section groups are lightweight summaries, not evidence models

They help organize the prompt, but they do not add much semantic depth by themselves.

## Detailed Plan To Fill The Gaps

## Planning Principles

The implementation plan should preserve the strengths of the current design:

- keep `StructuredAnswerContext` as the application-level evidence container
- keep deterministic renderers using typed context directly
- keep retrieval and evidence-preparation responsibilities where they already belong
- avoid new top-level architecture
- keep files small and single-responsibility

The goal is not to replace the current system wholesale.

The goal is to upgrade the generic LLM path so it consumes a richer structured evidence view with less duplication and better semantics.

## Phase 1. Introduce a prompt-facing structured evidence projection

### Goal

Stop making `AnswerPromptBuilder` render the raw internal model directly.

Add a dedicated prompt-facing projection layer so the system can preserve structure at the prompt boundary without coupling the prompt builder to every internal model detail.

### Why this phase matters

Right now `AnswerPromptBuilder` directly serializes:

- `maintenance_entries`
- `key_values`
- `structured_entities`
- groups
- raw sources

This mixes:

- evidence modeling
- prompt serialization
- duplication control
- prompt-shape policy

into one place.

### Proposed change

Add a dedicated prompt-context package under the existing answer-generation area, for example:

- `src/application/services/answer_generation/prompt_context/`

Suggested files:

- `prompt_evidence_bundle.py`
- `prompt_source_view.py`
- `prompt_entity_view.py`
- `prompt_table_view.py`
- `prompt_maintenance_view.py`
- `prompt_relationship_view.py`
- `prompt_context_projector.py`

### Responsibilities

`PromptContextProjector` should:

- accept `StructuredAnswerContext`
- normalize it into one prompt-facing evidence bundle
- remove prompt-level duplication
- keep source/entity/table/maintenance relationships explicit
- prepare a representation that can be rendered either as:
  - structured JSON-like text
  - compact textual blocks

### Important constraint

This projector is not a replacement for `StructuredAnswerContext`.

It is a prompt adapter only.

### Target files to update later

- `src/application/services/answer_generation/answer_generation_service.py`
- `src/application/prompts/answer_generation/answer_prompt_builder.py`

### Acceptance criteria

- `AnswerPromptBuilder` no longer walks raw `StructuredAnswerContext` directly
- prompt serialization is fed by one normalized prompt bundle
- duplication logic moves out of the prompt builder

## Phase 2. Replace flat prompt rendering with schema-structured evidence blocks

### Goal

Make the generic LLM see structured evidence as structured data, not only as formatted prose lines.

### Why this phase matters

This is the central fix for Gap 1.

Today the LLM sees:

- key-value lines
- entity lines
- relationship lines
- raw sources

That is readable, but semantically weak compared with a structured prompt payload.

### Proposed change

Change `AnswerPromptBuilder` so the organized evidence section becomes a machine-readable block.

Preferred order:

1. keep natural-language instructions
2. include a strict structured evidence payload
3. include a compact raw-source appendix only when needed

### Suggested prompt sections

- `Answer instructions`
- `Evidence schema`
- `Structured evidence payload`
- `Optional raw source appendix`

### Structured payload shape

The payload should explicitly separate:

- sources
- tables
- key_values
- maintenance_entries
- structured_entities
- relationships
- section_groups

Example shape idea:

```json
{
  "sources": [...],
  "tables": [...],
  "facts": [...],
  "maintenance_entries": [...],
  "entities": [...],
  "relationships": [...],
  "sections": [...]
}
```

The exact implementation can still be rendered as text, but it should preserve nested structure and arrays instead of reducing everything to sentence-like lines.

### Important design rule

Use one serializer dedicated to LLM-safe structured rendering.

Do not let `AnswerPromptBuilder` manually format nested structures inline.

Suggested helper files:

- `structured_prompt_serializer.py`
- `raw_source_appendix_builder.py`

### Acceptance criteria

- structured entities are rendered as nested objects, not comma-joined field strings
- relationships are rendered as explicit structured children
- maintenance entries are rendered as structured records
- table rows can be rendered as row arrays or named row objects

## Phase 3. Eliminate prompt-time parallel evidence representations

### Goal

Reduce duplication and prompt noise without losing recall.

### Why this phase matters

This addresses Gap 2 directly.

Today the same evidence may appear in:

- hydrated raw content
- `table_rows`
- `AnswerKeyValue`
- `AnswerMaintenanceEntry`
- `AnswerStructuredEntity`
- relationship-derived text

This is useful during extraction and deterministic rendering, but too noisy for prompt injection.

### Proposed change

Introduce an explicit evidence-canonicalization pass inside the new prompt projection layer.

Suggested file:

- `prompt_evidence_canonicalizer.py`

### Canonicalization rules

For prompt generation, each fact should have one primary representation:

- technical spec fact
  - prefer structured key/value or structured table row
- maintenance task/interval
  - prefer `AnswerMaintenanceEntry`
- spare part
  - prefer structured entity row
- manufacturer/supplier/contact
  - prefer structured entity plus contact relationship
- raw source content
  - keep only as supporting provenance or fallback appendix

### Important rule

Do not delete the parallel structures from `StructuredAnswerContext`.

Only canonicalize for prompt consumption.

The internal model can remain rich and redundant if that supports other consumers.

### Acceptance criteria

- each fact appears once in the main prompt evidence block
- raw source text is no longer the primary carrier for facts already modeled structurally
- prompt token pressure is reduced

## Phase 4. Preserve relationship semantics as graph structure

### Goal

Stop collapsing `AnswerRelationship` into human-readable text lines only.

### Why this phase matters

This addresses Gap 3.

The system already has typed relationship objects. The missing step is carrying them into the prompt with their structure intact.

### Proposed change

In the prompt-facing projection, represent relationships explicitly as graph edges.

Suggested shape:

- source entity id
- relationship type
- direction
- status
- confidence
- target entity id
- target entity type
- target fields

Suggested files:

- `prompt_relationship_graph_builder.py`
- `prompt_relationship_view.py`

### Additional improvement

Support grouping related entities into evidence families.

Examples:

- maintenance task -> procedure
- manufacturer -> contact point
- equipment -> specification
- spare part -> manufacturer

This helps the LLM understand local semantic neighborhoods instead of only isolated flat facts.

### Acceptance criteria

- prompt evidence contains explicit relationship objects
- relationships are no longer only embedded in string lines
- entity linkage remains visible even if raw source text is omitted

## Phase 5. Promote tables to first-class prompt evidence

### Goal

Expose tables explicitly to the generic LLM path.

### Why this phase matters

This addresses Gap 4.

The system already hydrates tables and preserves row grids, but the generic prompt path underuses them.

### Proposed change

Introduce a table projection step in the prompt bundle.

Suggested files:

- `prompt_table_projector.py`
- `prompt_table_row_normalizer.py`

### Table projection responsibilities

- read `AnswerSource.table_rows`
- map raw row arrays into normalized row objects when headers are available
- label table type when detectable
- preserve page/section/source provenance
- keep original row order

### Prompt behavior

For the generic LLM prompt, tables should be provided as:

- structured row objects for table-aware answers
- summarized table facts only when the answer format policy prefers summary mode

### Important rule

Do not rely on raw markdown tables alone.

The LLM should receive explicit row data when available.

### Acceptance criteria

- tables are emitted as first-class prompt evidence
- spare-parts/specification/certification tables no longer depend primarily on raw chunk text
- row-level provenance is preserved

## Phase 6. Upgrade source and section grouping into evidence topology

### Goal

Turn groups from lightweight summaries into meaningful evidence topology.

### Why this phase matters

This addresses Gap 5.

Current groups are useful labels, but they are not strong semantic guidance for the LLM.

### Proposed change

Replace prompt-time use of simple source/section groups with richer evidence topology views.

Suggested files:

- `evidence_topology_builder.py`
- `section_topology_view.py`
- `source_family_view.py`

### Topology ideas

Instead of only:

- chunk type group
- section-path group

build:

- source family
  - anchor chunk
  - companion chunks
  - same-section chunks
  - table companions
- section topology
  - parent section
  - current section
  - descendant detail sections
- evidence roles
  - direct evidence
  - supporting evidence
  - contextual evidence

### Benefit

This gives the LLM a much better model of:

- what is the main answer-bearing evidence
- what is supporting background
- which facts belong together

### Acceptance criteria

- prompt evidence distinguishes direct vs supporting evidence
- section structure is more than a string label
- source grouping helps answer synthesis instead of acting as a decorative summary

## Phase 7. Make raw source inclusion conditional and budget-aware

### Goal

Prevent raw source text from overpowering structured evidence.

### Why this phase matters

Even if the structured block improves, the prompt will still regress if large raw source dumps continue to dominate the token budget.

### Proposed change

Add raw-source inclusion policy logic driven by:

- answer intent
- evidence richness
- table availability
- structured entity availability
- token budget

Suggested files:

- `raw_source_inclusion_policy.py`
- `prompt_budget_allocator.py`

### Policy rules

- if structured evidence is rich, include only compact raw excerpts
- if structured evidence is sparse, allow larger raw source appendices
- if answer is table-driven, prefer structured table rows over raw chunk text
- if answer is maintenance-driven, prefer maintenance entries plus short supporting excerpts

### Acceptance criteria

- raw sources become supporting evidence, not the dominant prompt body
- structured payload gets first priority in the token budget
- prompt size becomes more stable across answer types

## Phase 8. Tighten answer-format policy so it consumes richer prompt evidence

### Goal

Ensure `AnswerFormatPolicy` benefits from the stronger evidence model.

### Why this phase matters

The answer format policy already reacts to:

- sparse evidence
- low-confidence evidence
- rich structured evidence
- multi-document evidence

But those signals are still coarse.

### Proposed change

Extend policy inputs using the prompt-facing evidence bundle.

Possible new signals:

- has_table_rows
- has_entity_graph
- has_direct_maintenance_records
- has_exact_identifier_rows
- has_only_supporting_evidence
- raw_source_dominant

Target file:

- `src/application/services/answer_generation/formatting/answer_format_policy.py`

### Acceptance criteria

- answer formatting instructions become more evidence-aware
- prompt structure and answer formatting policy reinforce each other

## Phase 9. Test strategy

### Unit tests to add

#### Prompt projection tests

- structured entities are projected without losing nested fields
- relationships are preserved as structured graph records
- maintenance entries remain structured
- tables are emitted as structured row evidence

#### Deduplication tests

- one fact does not appear in three parallel prompt sections
- raw source appendix excludes facts already promoted into structured sections

#### Prompt rendering tests

- generic LLM prompt includes structured payload block
- raw-source appendix is conditional
- prompt no longer relies on comma-joined entity strings as the only entity format

#### Policy tests

- rich structured table evidence changes prompt inclusion strategy
- sparse evidence still preserves enough raw context

### Integration tests to add

- `QuestionAnsweringWorkflow` builds richer structured prompt evidence from retrieved chunks
- deterministic renderers still behave unchanged
- generic LLM prompt path uses the new projection layer

## Phase 10. Recommended implementation order

### Pass A

- build prompt-facing projection layer
- do not change answer behavior yet

### Pass B

- switch prompt builder from direct model walking to projected bundle

### Pass C

- add structured serializer for entities, relationships, and tables

### Pass D

- add prompt-time canonicalization and raw-source inclusion policy

### Pass E

- upgrade groups into evidence topology

### Pass F

- expand tests and tune answer format policy

## Recommended first concrete change set

If this were implemented incrementally, the best first slice would be:

1. add `PromptContextProjector`
2. add prompt bundle models
3. migrate `AnswerPromptBuilder` to consume that bundle
4. keep current textual rendering format temporarily

That gives a safe internal seam first.

After that, the second slice should be:

1. structured serializer for entities and relationships
2. table-first prompt evidence
3. conditional raw-source appendix

That is the point where the generic LLM path would materially improve.

## Final planning verdict

The cleanest enterprise path is not to replace `StructuredAnswerContext`.

It is to insert a strong prompt-facing evidence projection layer between:

- `StructuredAnswerContext`
- `AnswerPromptBuilder`

That layer should:

- canonicalize evidence
- preserve relationships
- promote tables
- control raw-source inclusion
- expose topology rather than flat summaries

That is the most maintainable way to close the current gaps without breaking the rest of the answer architecture.

## Final Answer To The User's Question

## Is `StructuredAnswerContext` really structured?

Yes.

Internally it is a real structured evidence object with typed components, not just a string accumulator.

## Does it maintain structured evidence all the way into the LLM?

No, not fully.

Before the generic LLM call, `AnswerPromptBuilder` serializes that structure into human-readable prompt text.

So the current system:

- preserves structure in memory
- uses that structure directly for deterministic renderers
- flattens it into semi-structured text for the general LLM answer path

## Is it better than pure flattening?

Yes.

It is clearly better than only dumping retrieved chunks, because the prompt includes:

- normalized key-values
- maintenance-specific structured entries
- explicit entity and relationship summaries
- group summaries
- raw grounded sources

## Is it as strong as true structured evidence injection?

No.

If the goal is for the LLM to reason over evidence with stronger semantic fidelity, the current design stops one step short: it organizes structure well, but it does not preserve that structure as a true machine-readable prompt payload.

## Practical Verdict

The current implementation is:

- strong as an internal answer-context architecture
- moderate at preserving that structure into the generic LLM prompt
- not merely flat, but also not fully structured at inference time

The user concern is valid:

flattening does happen at the prompt boundary, and that does reduce some of the semantic advantages the internal model has already built.
