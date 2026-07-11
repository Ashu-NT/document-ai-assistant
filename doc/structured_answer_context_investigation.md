# StructuredAnswerContext Investigation Report

## Executive Conclusion

`StructuredAnswerContext` is not just a flat string container.

## Current Implementation Status

- Phase 1 is implemented:
  - prompt-facing projection now lives under
    `src/application/prompts/answer_generation/prompt_context/projectors/`
- Phase 2 is implemented:
  - the generic LLM path now emits `Evidence schema`,
    `Structured evidence payload`, and `Raw source appendix`
- Phase 3 is implemented:
  - prompt-time canonicalization now removes obvious entity/key-value duplication
    and keeps full raw content in the appendix instead of repeating it inside the
    main structured payload
- Phase 4 is implemented:
  - prompt-facing relationship graph edges and grouped evidence families are now
    emitted alongside entity records
- Phase 5 is implemented:
  - prompt-facing table evidence is now projected into first-class `tables`
    payload records with headers, normalized rows, row-level provenance, and
    top-level serialization instead of being duplicated inside payload `sources`
- Phase 6 is implemented:
  - prompt-facing evidence topology now emits `source_families` and
    `section_topology` so the generic LLM path sees direct, supporting, and
    contextual evidence roles rather than only lightweight group labels
- Phase 7 is implemented:
  - raw source appendix inclusion is now budget-aware and role-aware, so rich
    structured evidence leads the prompt while raw chunk text is trimmed down to
    the most relevant supporting excerpts
- Phase 8 is implemented:
  - answer-format policy context signals now distinguish richer evidence
    conditions such as table rows, entity graphs, direct maintenance records,
    exact identifier rows, and raw-source-dominant fallback cases
- Phase 9 is implemented:
  - the prompt-context path is now covered by dedicated table/topology/appendix
    tests plus workflow and answer-generation integration tests that exercise
    the real prompt builder and confirm the richer payload reaches the LLM path
- Phase 10 is implemented:
  - full validation now confirms the upgraded structured-answer-context path is
    green across the prompt, answer-generation, question-answering, and full
    `tests/unit` suite coverage used by this repo

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
- schema-structured at the prompt boundary
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
- `src/application/prompts/answer_generation/prompt_context/projectors/prompt_context_projector.py`
- `src/application/prompts/answer_generation/prompt_context/serializers/evidence_schema_formatter.py`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py`
- `src/application/prompts/answer_generation/prompt_context/appendix/raw_source_appendix_formatter.py`

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

`AnswerPromptBuilder` now creates three prompt-facing evidence sections:

1. `Evidence schema:`
2. `Structured evidence payload:`
3. `Raw source appendix:`

Relevant code:

- `src/application/prompts/answer_generation/answer_prompt_builder.py:55-99`
- `src/application/prompts/answer_generation/prompt_context/projectors/prompt_context_projector.py:14-89`
- `src/application/prompts/answer_generation/prompt_context/serializers/evidence_schema_formatter.py:6-19`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py:9-75`
- `src/application/prompts/answer_generation/prompt_context/appendix/raw_source_appendix_formatter.py:7-39`

### Evidence schema

This block is an explanatory contract for the model. It describes the main
evidence collections:

- sources
- key-values
- maintenance entries
- structured entities
- source groups
- section groups

It explains what each collection means, but it is not itself the evidence body.

### Structured evidence payload

This is the main evidence block for the generic LLM path.

It is emitted as JSON text and contains nested arrays/objects for:

- sources
- key-values
- maintenance entries
- structured entities
- relationship edges
- relationship families
- source groups
- section groups

This is materially stronger than the old line-based rendering because the model
now sees nested objects instead of only prose-like summaries.

### Raw source appendix

This block appends each source as text:

- source number
- document title
- section path
- pages
- raw content

So the LLM still gets the original chunk text after the structured payload.

## Does the current design preserve structure for the LLM?

### Yes, more than before

The LLM does receive evidence that is better structured than raw chunk dumping:

- maintenance entries as JSON records
- key-values are normalized
- structured entities stay nested
- entity relationships are explicit graph edges
- related semantic neighborhoods are grouped into evidence families
- source numbers and provenance remain visible
- canonicalized payload sources omit repeated raw content
- raw sources are still included for grounding

### But no, not in a fully structured sense

The LLM does not receive:

- the full internal `StructuredAnswerContext` object directly
- a fully topology-aware canonical evidence graph
- tables as a dedicated first-class top-level prompt section
- evidence topology such as direct/supporting/context roles

Instead, it receives a prompt-oriented JSON/text projection of those objects.

So the design is:

- semantically enriched
- schema-structured at the prompt boundary
- partially canonicalized, but not yet topology-rich

## Specific Observations About Flattening Quality

## 1. `structured_entities` are now preserved as nested payload objects

`AnswerPromptBuilder` no longer walks raw `structured_entities` directly.

Instead it:

- projects `StructuredAnswerContext` through `PromptContextProjector`
- serializes the prompt bundle through `StructuredEvidencePayloadSerializer`

Relevant code:

- `src/application/prompts/answer_generation/answer_prompt_builder.py:55-99`
- `src/application/prompts/answer_generation/prompt_context/projectors/prompt_context_projector.py:14-89`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py:45-75`

This is a clear improvement because entity fields and relationships remain
nested JSON objects instead of being reduced to comma-joined strings.

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

- table rows can now be emitted inside `sources[*].table_rows`
- but there is still no dedicated top-level `tables` section
- table evidence is still mixed inside source objects instead of being elevated
  into its own prompt evidence family

So the model receives more table structure than before, but table semantics are
still underexposed compared with a true first-class table payload.

## 3. Section and grouping structure is shallow

`SourceGroupBuilder` groups only by `chunk_type`.

`SectionGroupBuilder` groups only by the final `section_path` string.

Relevant code:

- `src/application/workflows/question_answering/answer_context/source_group_builder.py:12-27`
- `src/application/workflows/question_answering/answer_context/section_group_builder.py:12-50`

This is useful for organization, but it is not a deep semantic hierarchy.

## 4. The raw source block can dominate the context window

The prompt includes both:

- a structured JSON evidence payload
- full raw source text blocks

Relevant code:

- `src/application/prompts/answer_generation/answer_prompt_builder.py:55-99`
- `src/application/prompts/answer_generation/prompt_context/appendix/raw_source_appendix_formatter.py:7-39`

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

## Phase 9. Test strategy [Implemented]

### Unit coverage now in place

- prompt projection tests verify structured entities, nested relationship data,
  first-class tables, and projected prompt bundles
- canonicalization tests verify promoted structured evidence is not repeated
  noisily across payload sections
- appendix policy tests verify raw-source inclusion is conditional, role-aware,
  and budget-aware
- answer-format policy tests verify richer context signals affect prompt
  instructions deterministically

### Integration coverage now in place

- `QuestionAnsweringWorkflow` integration tests verify the real answer
  generation path carries relationship graphs into the prompt
- `AnswerGenerationService` integration tests verify the real prompt builder
  emits `tables`, `source_families`, `section_topology`, and a budgeted raw
  source appendix
- deterministic renderer tests remain green, so the richer LLM path did not
  regress the direct-rendering answers

## Phase 10. Full validation [Implemented]

### Validation performed

- targeted prompt / answer-generation / question-answering suites passed after
  the Phase 9 additions
- full `tests/unit` validation passed in the repo runtime used for this work

### Current validation result

- `tests/unit/application/prompts/answer_generation`
- `tests/unit/application/services/answer_generation`
- `tests/unit/application/workflows/question_answering`
- full `tests/unit` suite

All of the above are green with the structured prompt-context upgrades in
place.

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
