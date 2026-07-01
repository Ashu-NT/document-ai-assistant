# Identifier Architecture Review

**Date:** 2026-07-01  
**Scope:** Full-stack audit — domain model, extraction, persistence, retrieval, planning, answer generation  
**Verdict:** Identifiers are architecturally designed as first-class entities but are effectively orphaned — the creation path from ingestion to persistence is completely missing.

---

## Section 1 — Current Architecture

### Components Involved

| Layer | Component | File |
|---|---|---|
| Domain entity | `Identifier` | `src/domain/document/entities/identifier.py` |
| Domain enum | `IdentifierType` | `src/domain/common/enums.py` |
| Domain aggregate | `DocumentGraph.identifiers` | `src/domain/document/aggregates/document_graph.py` |
| Domain query | `RetrievalQuery.detected_identifiers` | `src/domain/retrieval/retrieval_query.py` |
| ORM | `IdentifierORM` | `src/infrastructure/db/orm_models/document_models.py` |
| Mapper | `IdentifierMapper` | `src/infrastructure/db/mappers/document/identifier_mapper.py` |
| Writer | `DocumentWriter._merge_chunk_artifacts` | `src/infrastructure/db/repositories/document/document_writer.py` |
| Reader | `DocumentReader.get_document_graph` | `src/infrastructure/db/repositories/document/document_reader.py` |
| Lookup | `IdentifierReader.search_identifiers` | `src/infrastructure/db/repositories/` |
| Service | `DocumentLookupService.search_identifiers` | `src/application/services/document/document_lookup_service.py` |
| Contract | `DocumentRepository.search_identifiers` | `src/application/contracts/document/document_repository.py` |
| Query extractor | `RetrievalQueryIdentifierExtractor` | `src/application/workflows/retrieval/retrieval_query_identifier_extractor.py` |
| Token extraction | `extract_identifier_tokens` | `src/application/workflows/retrieval/deduplication/retrieved_chunk_signature.py` |
| Query analyzer | `RetrievalQueryAnalyzer` | `src/application/workflows/retrieval/retrieval_query_analyzer.py` |
| Signal extractor | `RetrievalSignalExtractor` | `src/application/langgraph/retrieval_strategy/` |
| Strategy enum | `RetrievalStrategy.IDENTIFIER_LOOKUP` | `src/application/langgraph/retrieval_strategy/` |
| Strategy selector | `DeterministicStrategySelector` | `src/application/langgraph/retrieval_strategy/selectors/` |
| SQL retrieval | `SqlKeywordRepository` | `src/infrastructure/db/repositories/retrieval/sql_keyword_repository.py` |
| Vector retrieval | `QdrantVectorStore` | `src/infrastructure/retrieval/vector/qdrant_vector_store.py` |
| Qdrant payload | `QdrantPayloadMapper` | `src/infrastructure/retrieval/vector/qdrant_payload_mapper.py` |
| Guardrail | `IdentifierEvidenceGuardrail` | `src/application/guardrails/retrieval/identifier_evidence_guardrail.py` |
| Answer intent | `AnswerIntentAnalyzer` | `src/application/services/answer_generation/intent/answer_intent_analyzer.py` |
| Intent enum | `AnswerIntent.IDENTIFIER_LOOKUP` | `src/application/services/answer_generation/intent/answer_intent.py` |
| Prompt builder | `AnswerPromptBuilder` | `src/application/prompts/answer_generation/answer_prompt_builder.py` |
| Extraction workflow | `ExtractionWorkflow` | `src/application/workflows/extraction/extraction_workflow.py` |
| Extraction result | `ExtractionResult` | `src/domain/extraction/extraction_result.py` |

### What Is and Is Not Wired

**Wired (partial):**
- `Identifier` domain entity has full field set and normalization logic
- `IdentifierORM` exists with FK to documents, chunks, elements
- `IdentifierMapper` bidirectionally complete
- `DocumentWriter` writes and deletes identifiers as part of chunk artifact boundary
- `DocumentReader` loads identifiers when building document graph
- `IdentifierReader.search_identifiers()` performs indexed exact-match lookup
- `RetrievalQuery.detected_identifiers` carries regex-extracted tokens
- `IDENTIFIER_LOOKUP` retrieval strategy exists and is selected when identifier signals score ≥ 4.0
- SQL keyword retrieval searches detected identifier tokens with high weighting (24 pts content, 20 pts embedding_text)
- `IdentifierEvidenceGuardrail` validates all detected identifiers appear in retrieved chunks
- `AnswerIntent.IDENTIFIER_LOOKUP` exists and is detected from question terms

**Not wired (critical gaps):**
- No code path creates `Identifier` domain objects during ingestion or extraction
- `DocumentGraph.identifiers` is always empty in practice — the dict field exists but is never populated by any workflow
- `ExtractionWorkflow` extracts part numbers and serial numbers as embedded fields inside `EquipmentInfo` and `SparePart` — these are never promoted to `Identifier` entities
- Qdrant payload does not contain identifier fields — no vector-side identifier filter possible
- `IdentifierReader.search_identifiers()` is wired to a service and contract, but is never called from any retrieval execution path
- Resolved `Identifier` objects never reach `AnswerPromptBuilder` or `AnswerGenerationService`
- `DeterministicResearchPlanner` and `ResearchService` have zero identifier awareness
- `plan_executor.py` has no `IdentifierLookupTask` concept
- The retrieval plan builder falls back to `retrieve_chunks` when `retrieve_identifiers` tool is absent from the registry

---

## Section 2 — Identifier Lifecycle Trace

Tracing a single identifier: `A00168` (a part number found in a maintenance manual)

### PDF → Parser

`DoclingParser.parse()` converts the PDF to `RawParsedDocument`. The text `"A00168"` is embedded in a table row describing a spare part. No identifier extraction occurs at this stage.

### Parser → Canonical Elements

`DoclingDocumentNormalizer.normalize()` produces `CanonicalElement` objects. The table row becomes a `CanonicalElement` with `element_type=TABLE` or `element_type=TEXT`. `CanonicalElement` has no identifier field — `A00168` is raw text in the `.text` attribute.

**Step missing:** Parser and normalizer are pure structural transformers. No identifier extraction occurs here by design. This is correct.

### Canonical Elements → DocumentGraph

`DocumentGraphBuilder.build()` produces `DocumentGraph`. The element becomes part of a `DocumentChunk` covering the spare parts table. `DocumentGraph.identifiers` remains an empty dict `{}`.

**Step missing:** DocumentGraphBuilder does not perform identifier extraction. `A00168` is buried in chunk content text.

### DocumentGraph → ExtractionWorkflow

`ExtractionWorkflow.extract()` is called with final chunks. It calls `IdentifierExtractionPromptBuilder.build()` (misleadingly named) and sends a prompt to the LLM. The LLM returns structured JSON. Within the `spare_parts` array, `A00168` appears as:
```json
{
  "part_number": "A00168",
  "description": "...",
  "source_chunk_id": "chk_xyz"
}
```
This becomes a `SparePart` object inside `ExtractionResult`. 

**Step missing:** `SparePart.part_number = "A00168"` is NEVER promoted to an `Identifier` entity. `ExtractionResult` has no `identifiers: list[Identifier]` field. The `Identifier` domain entity is never instantiated.

### ExtractionResult → IdentifierORM

**Step entirely missing.** No code path converts `SparePart.part_number` → `Identifier` → `IdentifierORM`. The `identifiers` table remains empty for this document.

### DocumentGraph → Persistence (SQLite)

`DocumentWriter._merge_chunk_artifacts()` writes identifiers from `document_graph.identifiers`. Because that dict is empty, nothing is written. The `identifiers` table has zero rows for any document ingested through the current pipeline.

### SQLite → Qdrant

**Step does not apply.** Identifiers are not stored in Qdrant at all. `QdrantPayloadMapper.from_chunk()` writes: document_id, chunk_id, section_id, section_path, chunk_type, content, page_start, page_end, chunk_index. No identifier fields.

### Retrieval

When a user asks "What is part A00168?", `RetrievalQueryIdentifierExtractor.extract("What is part A00168?")` applies the regex `r"(?i)\b(?:[a-z]+[a-z0-9./-]*\d[a-z0-9./-]*|\d+(?:[./-]\d+)+)\b"` and extracts `["a00168"]` as a string token. This is stored in `RetrievalQuery.detected_identifiers = ["a00168"]`.

`DeterministicStrategySelector` detects the identifier signal (score 4.5) and selects `RetrievalStrategy.IDENTIFIER_LOOKUP`. The plan builder generates a retrieval step with query expansion: `"A00168 identifier part number serial number order code model"`.

`SqlKeywordRepository` searches for `%a00168%` across `ChunkORM.content`, `ChunkORM.embedding_text`, `DocumentORM.title` with 24 pt weighting. If `A00168` appears in any chunk's text content, it will be found. This works because the text is present in chunks, even though no Identifier entity was ever created.

`IdentifierReader.search_identifiers("A00168")` is **never called** from any retrieval node. The indexed lookup capability goes unused.

### Retrieval → Answer Generation

`IdentifierEvidenceGuardrail` checks that `"a00168"` appears in at least one retrieved chunk's `.content`. If found, retrieval proceeds.

`AnswerIntentAnalyzer` detects `AnswerIntent.IDENTIFIER_LOOKUP` from the question terms "part" and from the chunk content pattern. The intent string `"identifier_lookup"` is included in the answer prompt.

`AnswerPromptBuilder.build()` receives `answer_intent="identifier_lookup"` and includes it as a string. No structured `Identifier` object is injected. The model sees chunk text that happens to contain `A00168` but receives no resolved context like `{type: PART_NUMBER, normalized: "A00168", chunk: "chk_xyz", page: 42}`.

### Final Response

The model generates an answer based on chunk text. Citations are built from approved chunks. The response mentions the part number because it appeared in chunks, not because an identifier index was consulted.

**Summary of lifecycle gaps:**

| Step | Status |
|---|---|
| PDF → Parser | OK — structural parsing only |
| Parser → CanonicalElement | OK — no identifier role expected |
| CanonicalElement → DocumentGraph | OK — no identifier role expected here |
| DocumentGraph → ExtractionWorkflow | **GAP** — extraction produces SparePart.part_number, not Identifier entity |
| ExtractionResult → Identifier | **MISSING** — promotion step does not exist |
| Identifier → DocumentGraph | **MISSING** — graph.identifiers always empty |
| Identifier → SQLite (IdentifierORM) | **MISSING** — writer code exists but never called with data |
| SQLite → IdentifierReader lookup | **MISSING** — search_identifiers() never called in retrieval |
| Qdrant payload | **MISSING** — no identifier fields in vector payload |
| Retrieval → token detection | OK — regex tokens detected in query |
| Token → IDENTIFIER_LOOKUP strategy | OK — strategy selection works |
| Resolved Identifier → AnswerPrompt | **MISSING** — only intent string, not resolved objects |
| Identifiers → Deep Research | **MISSING** — no awareness |

---

## Section 3 — Ownership

### Candidates

**Parser:** Inappropriate. The parser is a structural transformer. It should not know about semantic identifier types. Identifier extraction requires contextual understanding of what `A00168` means (is it a part number? a drawing number? a certificate reference?).

**DocumentGraph:** Appropriate as a container and query surface (`get_chunk_identifiers`), but not as the creator. The graph represents parsed structure. Populating it with identifiers should happen after structural parsing, not during it.

**ExtractionWorkflow:** The strongest candidate but currently incomplete. It already uses an LLM to extract structured facts from chunks and already surfaces identifier-like values (`part_number`, `serial_number`, `model_number`) in its output. The workflow has the semantic context needed to determine identifier type. The gap is that it stops short of creating `Identifier` entities.

**Repository:** Inappropriate as owner. Repositories are persistence adapters, not business logic owners.

**Retrieval:** Inappropriate as owner. Retrieval consumes identifiers; it should not create them.

### Recommendation: ExtractionWorkflow is the sole creator

`ExtractionWorkflow` should own identifier creation for one reason: it is the only component that combines chunk text, LLM semantic reasoning, and structured output parsing in one place. It already extracts the raw material (`SparePart.part_number`, `EquipmentInfo.model_number`, `EquipmentInfo.serial_number`). It needs one additional step: promote those fields into `Identifier` entities and attach them to the result.

`DocumentGraph.identifiers` remains the authoritative runtime container — populated by the ingestion workflow after extraction runs, queried by retrieval and answer generation.

A secondary deterministic identifier extraction path should also exist for cases where extraction is disabled or for high-confidence pattern matches (drawing numbers, certificate IDs) that do not require LLM interpretation.

---

## Section 4 — Enterprise Architecture

### Enterprise Systems Standard

In enterprise CMMS (Computerized Maintenance Management Systems), PLM (Product Lifecycle Management), and technical documentation platforms, identifiers are never treated as optional metadata. They are the primary indexing key for equipment, parts, drawings, and certificates. Systems like SAP PM, IBM Maximo, and PTC Windchill are navigated almost entirely by identifier: equipment tag, part number, drawing revision.

In enterprise Document AI:
- Identifiers are **first-class semantic entities** — not extracted strings
- Each identifier has: type, normalized form, source location, confidence, relationships to other entities
- Identifier lookup is a **dedicated retrieval mode**, not a special case of semantic search
- Identifiers participate in **knowledge graph construction**: Part → Manufacturer, Drawing → Equipment, Certificate → Maintenance Task
- Answer generation receives **resolved identifier context** in addition to chunks: "Part A00168 is a filter element supplied by Alfa Laval, referenced on pages 42–44 of the maintenance section."

### Current Implementation Classification

The current implementation is **B — partially wired as a first-class entity at the schema level**, but treated operationally as option A (simple extracted metadata / raw text pattern matching).

The schema (domain entity, ORM, mapper, strategy, guardrail, intent) was designed with enterprise intent. The implementation stopped before closing the loop from extraction to persistence to structured retrieval.

The correct target is option B throughout the entire stack: each identifier is a persistent, typed, normalized, location-aware, relationship-bearing semantic entity that participates in all retrieval and reasoning paths.

---

## Section 5 — Extraction Audit

### What ExtractionWorkflow Extracts

**Method:** `ExtractionWorkflow.extract(chunks: list[DocumentChunk]) -> ExtractionResult`

**Mechanism:** LLM-based. `IdentifierExtractionPromptBuilder.build()` constructs a prompt asking the model to return JSON containing `maintenance_tasks`, `spare_parts`, `equipment`, and `manufacturers`. The prompt includes chunk text as context.

**Identifier-like fields extracted within the LLM output:**
- `spare_parts[].part_number` — unvalidated string
- `equipment[].model_number` — unvalidated string
- `equipment[].serial_number` — unvalidated string
- `manufacturers[].name` — string (not a typed entity)

**Confidence values:** Yes — per-item `confidence_score: float` and `requires_human_review: bool` on each extracted entity.

**Validation:** `ExtractionResultValidator` validates structure and required fields. No normalization or type classification of identifier-like strings.

**Duplicate handling:** None at the identifier level. If two chunks both mention part number `A00168`, the extraction may produce two separate `SparePart` objects with the same `part_number`. No deduplication across chunks.

**Normalization:** None. `SparePart.part_number = "A 00168"` and `SparePart.part_number = "A00168"` are treated as different values. The `Identifier` domain entity has `normalize_identifier()` (`.strip().upper().replace(" ", "")`) but this is never applied to extraction output.

**What is NOT extracted:**
- `IdentifierType` classification — all identifier-like strings are untyped within ExtractionResult
- Drawing numbers
- Certificate numbers
- Component codes
- Section or page location of the identifier

### The Naming Confusion

`IdentifierExtractionPromptBuilder` is misleadingly named. It extracts maintenance domain data, not `Identifier` domain entities. This name creates false confidence that the identifier pipeline is functional when it is not.

---

## Section 6 — Domain Model

### Identifier (`src/domain/document/entities/identifier.py`)

```
identifier_id: str
document_id: str
raw_value: str
identifier_type: IdentifierType  (PART_NUMBER | SERIAL_NUMBER | MODEL_NUMBER | DRAWING_NUMBER | COMPONENT_CODE | UNKNOWN)
chunk_id: str | None
element_id: str | None
normalized_value: str | None     (auto-computed: strip().upper().replace(" ",""))
confidence_score: float | None
audit: AuditMetadata
```

**Assessment:** Sufficient field set. Normalization logic is correct. `identifier_type` enum covers the main industrial document types. Missing: `section_id`, `page_start`, `page_end` for direct location reference without going through the chunk join.

**Recommended additions:**
- `section_id: str | None` — direct section link for faster section-scoped queries
- `page_start: int | None` and `page_end: int | None` — direct page location
- `source: IdentifierSource` — enum (LLM_EXTRACTION | DETERMINISTIC_PATTERN | HYBRID) for provenance tracking

### IdentifierORM

Columns: id, document_id (FK+idx), chunk_id (FK+idx, nullable), element_id (FK+idx, nullable), raw_value, normalized_value (idx), identifier_type, confidence_score, created_at.

**Missing:** section_id, page_start, page_end. Page and section info must be retrieved by joining through chunk or element.

**Recommended additions:** Add `section_id`, `page_start`, `page_end` columns with appropriate indexes. This enables "find all part numbers mentioned on page 42" without a join chain.

### IdentifierRepository / IdentifierReader

`IdentifierReader.search_identifiers(value: str) -> list[Identifier]` — exact normalized match. Works correctly for known-exact lookup.

**Missing capabilities:**
- Prefix/fuzzy search: `search_identifiers_like(prefix: str)` for partial matches like "MB-" → all MB-series parts
- Type-filtered lookup: `search_by_type(identifier_type: IdentifierType, document_id: str)`
- Chunk-scoped lookup: `get_identifiers_for_chunk(chunk_id: str)` — currently only in-memory via DocumentGraph
- Page-scoped lookup: `get_identifiers_on_page(document_id: str, page: int)`

### IdentifierService

Currently: `DocumentLookupService.search_identifiers()` is a thin delegate. There is no dedicated `IdentifierService`.

**Recommended:** Promote to a standalone `IdentifierService` with lookup, type-filtered search, page-scoped query, and identifier resolution (returning identifier + associated chunk + section context).

### DocumentGraph

`identifiers: dict[str, Identifier]` — container exists. `get_chunk_identifiers(chunk_id)` method exists. `clear_chunk_dependents()` clears identifiers correctly.

**Assessment:** Correct design. Container is appropriate here. Population path is missing (see Section 7).

### DocumentChunk

No direct identifier reference. Identifiers link back to chunks via `Identifier.chunk_id`.

**Assessment:** Acceptable. The FK direction (Identifier → Chunk) is correct for a one-to-many relationship (one chunk can contain many identifiers). No change needed here.

### CanonicalElement

No identifier fields. Correct — canonical elements are structural parsing outputs, not semantic entities.

---

## Section 7 — DocumentGraph

### Why It Exists

`DocumentGraph.identifiers: dict[str, Identifier]` was designed to hold the complete set of typed, normalized, location-aware identifiers extracted from a document — the same way `DocumentGraph.chunks` holds finalized chunk payloads. It is the runtime aggregate that answers "what identifiers does this document contain, and where?"

The `get_chunk_identifiers(chunk_id)` method exists specifically to support retrieval augmentation: "for these retrieved chunks, what identifiers do they contain?" This is architecturally correct and should be preserved.

### Who Should Populate It

`ExtractionWorkflow` should populate it. After extraction runs, a promotion step converts `SparePart.part_number`, `EquipmentInfo.model_number`, `EquipmentInfo.serial_number` into `Identifier` entities and appends them to `document_graph.identifiers`. A secondary deterministic pass can scan all chunk text for high-confidence patterns (drawing numbers, certificate references) and add additional identifiers.

`IngestionWorkflow.run()` then calls `DocumentWriter._merge_chunk_artifacts()`, which already writes `document_graph.identifiers` to the database — this write path is complete and correct. No change needed to the writer.

### Should It Remain?

Yes. `DocumentGraph.identifiers` should remain. It is the correct aggregate surface for identifier queries. Removing it would require inventing a separate lookup mechanism with the same semantics.

### Should It Move?

No. Its position in the domain aggregate is correct.

### Should It Become Immutable?

After the write to persistence, yes. Identifiers for a document should be frozen until reingest is triggered. The `clear_chunk_dependents()` method already handles the mutable lifecycle correctly during graph replacement.

---

## Section 8 — Persistence

### How Identifiers Are Stored

`IdentifierORM` table schema:

```
id               (PK)
document_id      (FK → documents.id, indexed)
chunk_id         (FK → chunks.id, nullable, indexed)
element_id       (FK → elements.id, nullable, indexed)
raw_value        (not null)
normalized_value (not null, indexed)
identifier_type  (not null)
confidence_score (nullable)
created_at       (not null)
```

Relationships as implemented:

```
Document
  └─ Identifier (via document_id FK)
       └─ Chunk (via chunk_id FK, nullable)
            └─ Element (via element_id FK, nullable)
```

Section and Page are NOT directly represented. To get the page for an identifier, the caller must join through Chunk and read `ChunkORM.page_start`.

### Should Identifiers Reference Page, Section, Chunk, Document, All?

**Document** — Yes, always. The document FK is the primary scoping key. Already present.

**Chunk** — Yes, always when extraction is chunk-scoped. Identifiers extracted from a specific chunk should reference that chunk. Already present. Should be made non-nullable for extraction-derived identifiers (those without a chunk_id would be a data quality issue).

**Element** — Conditionally. When the identifier is found in a specific table cell or text span, element-level provenance is valuable for citation accuracy. Already present. Keep nullable.

**Section** — Yes, should be added. Many queries are section-scoped: "find all part numbers in the maintenance section." Currently requires joining through chunk → section. Adding `section_id` to `IdentifierORM` as a nullable FK (mirroring the chunk FK pattern) eliminates that join for the common case.

**Page** — Yes, should be added as a denormalized pair `(page_start, page_end)` on `IdentifierORM`. Page is the primary user-facing location indicator ("Part A00168 is mentioned on page 42"). Avoiding the join is worth the denormalization. This matches how `QdrantPayloadMapper` already denormalizes page onto the vector payload.

### Recommended Relationship Model

```
Document
  └─ Identifier
       ├─ document_id (FK, non-nullable)
       ├─ chunk_id    (FK, non-nullable for extraction-derived; nullable for document-level detection)
       ├─ element_id  (FK, nullable)
       ├─ section_id  (FK, nullable)  ← ADD
       ├─ page_start  (int, nullable)  ← ADD (denormalized)
       └─ page_end    (int, nullable)  ← ADD (denormalized)
```

---

## Section 9 — Retrieval

### Current Identifier Participation in Retrieval

**Query-level (works):**
1. `RetrievalQueryIdentifierExtractor` extracts token strings (regex) from query text
2. `RetrievalQuery.detected_identifiers = ["a00168"]` carries these tokens
3. `SqlKeywordRepository` includes identifier tokens as high-weight LIKE patterns (24 pts content, 20 pts embedding_text)
4. `IdentifierEvidenceGuardrail` validates all tokens appear in retrieved chunks

**Strategy-level (works):**
1. `RetrievalSignalExtractor` scores identifier signals at 4.0–4.5
2. `DeterministicStrategySelector` maps to `IDENTIFIER_LOOKUP` strategy
3. Query expansion adds "identifier part number serial number order code model"
4. Chunk type preferences: TECHNICAL_SPECIFICATION, SPARE_PARTS_TABLE, CERTIFICATION_INFO, DRAWING_REFERENCE

**Index-level (does NOT work):**
- `IdentifierReader.search_identifiers("A00168")` returns matching `Identifier` entities from the indexed `normalized_value` column
- This lookup is **never called** from any retrieval node
- The identifiers table is empty because no creation path exists, so even if it were called, it would return nothing

**Vector-level (does NOT work):**
- Qdrant payload has no identifier fields
- `QdrantVectorStore._build_filter()` cannot filter by identifier value
- Identifier search is limited to semantic similarity of chunk content

### Can the System Answer These Queries?

| Query | Result | How |
|---|---|---|
| "Find A00168" | Partial — works if A00168 appears in chunk text | SQL keyword LIKE matching on chunk content |
| "Find MB-2" | Partial — same mechanism | SQL keyword LIKE matching |
| "Find HAM2423501" | Partial — same | SQL keyword LIKE matching |
| "Find Alfa Laval" | Partial — manufacturer name, no identifier | Semantic search only |
| "Find supplier" | Weak — generic term | Semantic search; chunk type filtering |
| "Find manufacturer" | Weak — generic term | Semantic search; chunk type filtering |
| "Find drawing number" | Weak — general intent detected | IDENTIFIER_LOOKUP strategy; keyword search |
| "Find certificate" | Weak — semantic only | CERTIFICATION_INFO chunk type filter |
| "Find serial number" | Weak — general intent detected | Keyword search |

**Root cause:** All retrieval falls back to chunk text matching. If the identifier appears verbatim in chunk text, it will be found. If it appears only in structured data (e.g., a table column header not embedded in content text), it may not be found. The identifier index, which would enable exact, type-filtered, page-precise lookup, is unused.

---

## Section 10 — Retrieval Strategy

### Does IDENTIFIER_LOOKUP Already Exist?

Yes. `RetrievalStrategy.IDENTIFIER_LOOKUP` exists in the strategy enum. `DeterministicStrategySelector` maps the "identifier" signal category to this strategy. The strategy is selected when identifier signal score ≥ 4.0.

### Should Finer-Grained Strategies Exist?

The current single `IDENTIFIER_LOOKUP` strategy is the right level of granularity for strategy selection. Splitting it into PART_NUMBER_LOOKUP, SERIAL_LOOKUP, CERTIFICATE_LOOKUP, etc. at the strategy level would add complexity without retrieval benefit — the retrieval mechanism (identifier index query + chunk text search) is the same regardless of type.

Type-level differentiation should instead happen at the **execution** level through `IdentifierType` filtering on `IdentifierReader.search_identifiers()`. The correct model is:

```
RetrievalStrategy.IDENTIFIER_LOOKUP
    → IdentifierReader.search_identifiers(value, type_filter=PART_NUMBER)
    → returns matching Identifier entities with chunk_id, section_id, page
    → fetch associated chunks from those locations
    → deliver type-aware, location-precise result
```

`ENTITY_LOOKUP` as a distinct strategy is worth considering for manufacturer/supplier queries that are not part-number structured — these are better served by full-text search on the manufacturers table or through the `ExtractionResult.manufacturers` repository rather than the identifier index.

---

## Section 11 — Hybrid Retrieval Order

### Should Identifier Lookup Happen Before or After Semantic Retrieval?

**For deterministic identifier queries (exact known value):**

When the query is `"Find part A00168"` or `"What is MB-2?"`, the identifier value is known and exact. The correct order is:

1. **First: Identifier index lookup** — query `IdentifierReader.search_identifiers("A00168")`, retrieve the matching `Identifier` entities with their chunk IDs and page numbers
2. **Then: Targeted chunk fetch** — retrieve the specific chunks that contain this identifier (known chunk_ids, no need for semantic search)
3. **Optionally: Semantic expansion** — fetch nearby chunks for additional context using the same section as the identifier's location

Embedding search should not be the primary mechanism for known-identifier queries. It introduces noise from semantically similar but unrelated content.

**For entity queries (manufacturer name, supplier type):**

When the query is `"Who is the manufacturer?"` or `"Find Alfa Laval"`, semantic retrieval should run first, with the extraction result tables (manufacturers, equipment) providing structured augmentation.

**Implementation:** The `RetrievalPlanBuilder` already generates a plan with a preferred tool `"retrieve_identifiers"`. That tool needs to be implemented in the tool registry to call `IdentifierReader.search_identifiers()` and return results directly, before the hybrid embedding + keyword search runs as a fallback or supplement.

---

## Section 12 — Planning

### Does the Planner Detect Identifier Queries?

**`DeterministicResearchPlanner`:** No. Its `_CATEGORY_PATTERNS` regex covers troubleshooting, maintenance, procedure, specification, certification, drawing, figure, table — but not identifier patterns. A query like `"Find all maintenance tasks mentioning MB-2"` would not be recognized as identifier-augmented research.

**`plan_executor.py`:** No `IdentifierLookupTask`. Task types are: format_combined_answer, list_documents, find_document, document_details, explore_document, retrieve_chunks, answer_question, run_quality_gate, retrieval_trace.

### Should the Planner Detect Identifier Queries?

Yes, but at the correct layer. The planner should detect identifier queries and:

1. Generate a `retrieve_identifiers` step that calls `IdentifierReader.search_identifiers()` directly
2. Use the returned `Identifier` objects (with chunk_id, section_id, page) to scope the subsequent chunk retrieval to known locations
3. Skip broad semantic retrieval when exact identifier matches are found

The correct model:

```
User: "Find all maintenance tasks mentioning A00168"

Planner:
  Step 1: retrieve_identifiers("A00168")          → Identifier(chunk_id="chk_x", page=42)
  Step 2: retrieve_chunks(document_id, chunk_id="chk_x", expand_context=True)
  Step 3: answer_question(question, chunks)
```

This requires adding `IdentifierLookupTask` to `plan_executor.py` that calls `DocumentLookupService.search_identifiers()` and returns chunk IDs for downstream retrieval.

---

## Section 13 — Deep Research

### Do Identifiers Currently Participate in Research?

No. `ResearchService.plan_research()` uses `DeterministicResearchPlanner` whose category patterns do not include identifier patterns. `ResearchService.execute_research()` calls `ResearchTaskExecutor` which runs standard hybrid retrieval — no identifier index access. `ResearchService.evaluate_research()` and `synthesize_research()` have no identifier awareness.

### Should Identifiers Accelerate Research?

Yes, significantly. When a research goal references a known identifier, the research plan should use it as a retrieval anchor:

**Example: "Compare all references to MB-2"**

Without identifier index: semantic search for "MB-2" across all chunks, relying on exact text match in embedding space.

With identifier index:
1. `search_identifiers("MB-2")` → all `Identifier` entities for MB-2 → list of (chunk_id, section_id, page)
2. Research tasks fetch those specific chunks directly — precision retrieval, no semantic noise
3. Additional context fetched by expanding around those known locations

**Example: "Find every maintenance task mentioning A00168"**

The identifier index returns all chunks where A00168 is recorded. The research executor fetches exactly those chunks and applies the maintenance task filter via chunk type. The result is faster, more complete, and more precise than embedding-based search alone.

The research planner should detect identifier patterns (same regex as `RetrievalQueryIdentifierExtractor`) and generate `IDENTIFIER_ANCHOR` research tasks that pre-fetch identifier locations before executing semantic research tasks.

---

## Section 14 — Answer Generation

### Does Answer Generation Currently Receive Resolved Identifier Objects?

No. The pipeline currently delivers:
- `answer_intent = "identifier_lookup"` (string in prompt)
- Retrieved chunks (whose content may contain the identifier as text)
- Citations built from chunk metadata

`AnswerGenerationService.generate()` receives `AnswerGenerationRequest`. This request has no field for resolved `Identifier` objects. `AnswerPromptBuilder.build()` injects the intent string and chunk text — no structured identifier context.

### Should the Answer Prompt Receive Resolved Identifier Objects?

Yes. In an enterprise system, the answer for "What is part A00168?" should be:

```
Part Number: A00168
Type: Spare Part
Normalized: A00168
Location: Page 42, Maintenance Section 7.3
Source Chunk: "Replace filter element A00168 every 500 operating hours"
Confidence: 0.95
```

Not just: whatever the model infers from reading chunk text that happens to contain "A00168".

**Recommended change:** Add `resolved_identifiers: list[Identifier]` to `AnswerGenerationRequest`. `AnswerPromptBuilder` adds an `Identifiers` section before the raw sources block when identifiers are present:

```
Identifiers resolved:
• A00168 [PART_NUMBER] — page 42, section "Spare Parts List"
```

This gives the model structured location-aware context rather than relying on text occurrence, and enables accurate citation attribution at the identifier level.

---

## Section 15 — Future Knowledge Graph

### Do Identifiers Naturally Become Nodes?

Yes. The current domain model already contains the raw material for a knowledge graph. Each `Identifier`, `ExtractionResult`, `SparePart`, `EquipmentInfo`, `Manufacturer`, `MaintenanceTask`, `DocumentChunk`, and `DocumentSection` is a potential node. The relationships already exist as foreign keys:

```
Document ─────────────────────────────────────────── DocumentGraph
    │                                                       │
    ├─ Identifier (PART_NUMBER: A00168)                    │
    │       └─ links to Chunk → Section → Page            │
    │                                                       │
    ├─ SparePart (part_number: A00168)                     │
    │       ├─ used_in: EquipmentInfo (model: FWC-12)      │
    │       └─ sourced_from: Manufacturer (Alfa Laval)     │
    │                                                       │
    ├─ MaintenanceTask (interval: 500h)                    │
    │       └─ references: SparePart (A00168)              │
    │                                                       │
    └─ DrawingReference (DRAWING_NUMBER: MB-2)            │
            └─ links to Section (section 7.3)              │
```

If identifiers are promoted to first-class entities with section and page denormalization, and if the `Identifier ↔ SparePart` link is materialized (the `SparePart.part_number` that was the source of an `Identifier(PART_NUMBER, "A00168")` should be traceable back to each other), the system has the scaffolding for a knowledge graph without a new data store.

Phase 1 of a knowledge graph is simply: make the existing relational links navigable from the retrieval layer. Full graph semantics (RDF, property graphs, LLM-guided traversal) are a later concern.

---

## Section 16 — Recommended Architecture

### Target Flow

```
PDF
  ↓
DoclingParser.parse()
  → RawParsedDocument

  ↓
DoclingDocumentNormalizer.normalize()
  → CanonicalElement[]   (no change)

  ↓
DocumentGraphBuilder.build()
  → DocumentGraph (provisional)
  → DocumentGraph.identifiers = {}   (still empty; correct)

  ↓
PostClassificationChunkFinalizationWorkflow
  → Final DocumentChunk[]

  ↓
ExtractionWorkflow.extract()
  → ExtractionResult (maintenance tasks, spare parts, equipment, manufacturers)
  → NEW: IdentifierPromotionService.promote(extraction_result, chunks)
       → creates Identifier entities from:
            SparePart.part_number          → Identifier(PART_NUMBER)
            EquipmentInfo.model_number     → Identifier(MODEL_NUMBER)
            EquipmentInfo.serial_number    → Identifier(SERIAL_NUMBER)
       → deduplicates by normalized_value
       → attaches chunk_id, element_id, page_start, page_end, section_id

  ↓
DeterministicIdentifierScanner.scan(chunks)
  → Identifier entities from high-confidence regex patterns
       (drawing numbers: r"DRG[-\s]?\d+", certificate: r"CERT[-\s]?\d+", etc.)
  → merged with promoted identifiers; deduplication by normalized_value

  ↓
IngestionWorkflow wires both sources:
  document_graph.identifiers = {id: identifier for identifier in all_identifiers}

  ↓
DocumentWriter._merge_chunk_artifacts()
  → writes IdentifierORM rows (THIS ALREADY WORKS — just needs data to write)

  ↓
SQLite: identifiers table populated

  ↓
Qdrant: add identifier payloads to vector points
  → chunk payload extended with:
       "identifier_values": ["a00168", "mb-2"]   (normalized, from associated identifiers)
  → enables Qdrant filter by identifier presence

  ↓
IdentifierIndex operational:
  → IdentifierReader.search_identifiers("A00168") returns Identifier entities
  → IdentifierReader.search_by_type(PART_NUMBER, document_id) returns typed results
  → IdentifierReader.get_identifiers_on_page(document_id, page=42) works

  ↓
Retrieval:
  → IDENTIFIER_LOOKUP strategy now calls retrieve_identifiers tool (real implementation)
  → tool calls IdentifierReader.search_identifiers()
  → returns Identifier entities with chunk_id, page, section
  → RetrievalWorkflow fetches those specific chunks by known location
  → HybridRetrievalService runs as supplement (not primary) for context expansion

  ↓
Planner:
  → DeterministicResearchPlanner detects identifier patterns
  → generates IdentifierLookupTask
  → PlanExecutor resolves IdentifierLookupTask via DocumentLookupService.search_identifiers()

  ↓
AnswerGenerationRequest:
  → resolved_identifiers: list[Identifier]  (NEW field)
  → answer_intent: IDENTIFIER_LOOKUP

  ↓
AnswerPromptBuilder:
  → injects structured Identifiers block before raw sources
  → model receives typed, location-aware context

  ↓
Final Response:
  → citation includes page, section, identifier type
  → answer is precise, grounded, location-referenced
```

---

## Section 17 — Implementation Plan

### P0 — Critical Fixes (close the creation gap)

**P0.1 — IdentifierPromotionService**

Create `src/application/services/document/identifier_promotion_service.py::IdentifierPromotion Service`.

- Input: `ExtractionResult`, `list[DocumentChunk]`
- Output: `list[Identifier]`
- Logic: For each `SparePart`, create `Identifier(PART_NUMBER, part_number, chunk_id=source_chunk_id, confidence_score=spare_part.confidence_score)`. Same for `EquipmentInfo.model_number` → `MODEL_NUMBER`, `EquipmentInfo.serial_number` → `SERIAL_NUMBER`.
- Deduplication: by `normalized_value` + `identifier_type` combination
- Chunk linkage: use `source_chunk_id` already present in extraction result entities to attach `chunk_id`, then look up `page_start`/`page_end` from the chunk

**P0.2 — Wire IdentifierPromotion into IngestionWorkflow**

In `src/application/workflows/ingestion/ingestion_workflow.py`, after `ExtractionWorkflow.extract()`, call `IdentifierPromotionService.promote()`. Assign results to `document_graph.identifiers`.

**P0.3 — Add section_id, page_start, page_end to IdentifierORM**

Add three columns to `IdentifierORM`. Create an Alembic migration. Update `IdentifierMapper` bidirectionally. Update `Identifier` domain entity with the three new fields.

**P0.4 — Tests**

- `tests/unit/application/services/document/test_identifier_promotion_service.py` — verify part_number → Identifier(PART_NUMBER), deduplication, chunk linkage
- `tests/unit/application/workflows/ingestion/test_ingestion_workflow_identifier_creation.py` — verify identifiers populated in graph and written via DocumentWriter after extraction

### P1 — Architecture Cleanup

**P1.1 — DeterministicIdentifierScanner**

Create `src/application/workflows/ingestion/deterministic_identifier_scanner.py`. Scan chunk text for high-confidence non-LLM patterns:
- Drawing numbers: `r"\b(?:DRG|DWG)[-\s]?\d{3,}\b"`
- Certificate numbers: `r"\b(?:CERT|ISO|EN)\s*[-\s]?\d{3,}\b"`
- Component codes matching known prefixes from document classification

Wire into ingestion workflow after extraction, merging with promoted identifiers and deduplicating.

**P1.2 — retrieve_identifiers tool**

Implement `src/application/tools/retrieval/retrieve_identifiers_tool.py`. This tool is already referenced by name in `RetrievalPlanBuilder` when `IDENTIFIER_LOOKUP` strategy is selected. Currently falls back to `retrieve_chunks` because the tool is absent from the registry. The tool should call `DocumentLookupService.search_identifiers()`, return matching `Identifier` entities, and provide the chunk IDs for targeted retrieval.

**P1.3 — IdentifierLookupTask in PlanExecutor**

Add `IdentifierLookupTask` to `plan_executor.py` task dispatch. When a plan step requests identifier lookup, call `DocumentLookupService.search_identifiers(value)` and update state with `resolved_identifiers`.

**P1.4 — IdentifierService**

Promote `DocumentLookupService.search_identifiers()` into a dedicated `IdentifierService` with: `search(value)`, `search_by_type(type, document_id)`, `get_for_chunk(chunk_id)`, `get_on_page(document_id, page)`.

**P1.5 — Rename IdentifierExtractionPromptBuilder**

Rename to `ExtractionPromptBuilder` to eliminate naming confusion. The current name implies it extracts `Identifier` entities when it extracts maintenance domain data.

### P2 — Retrieval Improvements

**P2.1 — resolved_identifiers in AnswerGenerationRequest**

Add `resolved_identifiers: list[Identifier]` to `AnswerGenerationRequest`. Update `AnswerPromptBuilder` to inject an Identifiers block. Update `answer_question_node.py` to pass resolved identifiers from state.

**P2.2 — Qdrant identifier payload**

Extend `QdrantPayloadMapper.from_chunk()` to include `"identifier_values": list[str]` (normalized values of all identifiers whose `chunk_id` matches this chunk). Requires passing the document's identifier index into the mapper at embedding time. Add Qdrant filter support for `identifier_values` in `QdrantVectorStore._build_filter()`.

**P2.3 — DeterministicResearchPlanner identifier patterns**

Add identifier category patterns to `_CATEGORY_PATTERNS` in `DeterministicResearchPlanner`. When the research goal contains identifier tokens, generate a pre-fetch identifier lookup task before semantic research tasks.

**P2.4 — IdentifierReader additional methods**

Add: `search_by_type`, `get_identifiers_for_chunk`, `get_identifiers_on_page` to `IdentifierReader` and expose through `IdentifierService`.

### P3 — Knowledge Graph Preparation

**P3.1 — Identifier ↔ SparePart cross-link**

Add `identifier_id: str | None` to `SparePartORM`. When `IdentifierPromotionService` creates an `Identifier` from a `SparePart`, store the identifier's ID back on the SparePart. This creates the bidirectional link needed for graph traversal.

**P3.2 — Identifier ↔ MaintenanceTask cross-link**

If a maintenance task references a part number, record that link. `MaintenanceTask` and `Identifier` become connected nodes.

**P3.3 — Graph traversal service**

`IdentifierGraphService.resolve(identifier_value: str, document_id: str) -> IdentifierContext`:
- Returns: the Identifier entity, its associated SparePart or EquipmentInfo, its associated MaintenanceTask references, its chunk, section, and page
- Used by answer generation to build a fully resolved identifier context block

---

## Section 18 — Risks

### Risk 1: Silent failure of identifier lookup (P0 — Critical)

Because the identifiers table is always empty, `IdentifierReader.search_identifiers()` always returns `[]`. Any query asking for a specific part number, serial number, or drawing number falls through to chunk text matching. If the identifier appears in a table that was not correctly embedded, or in a section that scored below the retrieval threshold, the system returns no result or a wrong result. The user experience is: the system "doesn't know" the part number, even though it was extracted by the LLM.

### Risk 2: Identifier type information is permanently lost (P0 — Critical)

`ExtractionWorkflow` determines that `"A00168"` is a `part_number` (from the JSON schema it sends to the LLM). This type information is embedded in `SparePart.part_number`. When it is not promoted to `Identifier(PART_NUMBER, "A00168")`, the type is discarded. Future queries cannot distinguish "find drawing number MB-2" from "find part number MB-2" — both would match the same text patterns.

### Risk 3: Duplicate detection failures during reingest (P1)

If identifiers are later wired correctly but without deduplication, multiple ingestion runs of the same document will produce duplicate `IdentifierORM` rows. The `replace_document_chunk_artifacts` path does handle deletion, but the deduplication logic within the promotion service must also operate correctly before the graph is written.

### Risk 4: Answer hallucination for identifier queries (P2)

Without resolved identifier context in the answer prompt, the model infers identifier metadata from chunk text. It may generalize incorrectly: if a chunk says "use filter element A00168 or equivalent," the model might assert A00168 has properties it inferred from "equivalent" parts. Structured identifier context anchors the answer to exactly what was stated.

### Risk 5: IDENTIFIER_LOOKUP strategy selects a non-existent tool (P1)

`RetrievalPlanBuilder` references tool `"retrieve_identifiers"` when the IDENTIFIER_LOOKUP strategy is selected. If that tool is absent from the registry (which it currently is), the plan falls back to `"retrieve_chunks"`. This fallback silently degrades the identifier query path. A user running `--show-retrieval-strategy` would see `IDENTIFIER_LOOKUP` selected while the actual execution runs generic chunk retrieval.

### Risk 6: Knowledge graph opportunity cost (P3)

The relational model already has the right structure to support a lightweight knowledge graph (Document → Identifier → SparePart → Manufacturer, MaintenanceTask → SparePart). Continuing to treat identifiers as incidental text strings rather than entity nodes forecloses this path. Each quarter without materializing the cross-links makes the eventual graph construction harder as schema assumptions accumulate.

---

## Section 19 — Acceptance Criteria

Identifiers are enterprise-ready only when all of the following are true:

| Criterion | Current State | Required |
|---|---|---|
| Extraction has clear ownership | `ExtractionWorkflow` identified as owner; promotion step missing | Add `IdentifierPromotionService`, wire into `ExtractionWorkflow` result |
| `DocumentGraph.identifiers` is populated | Always empty — no creation path | Wire promotion step, confirm graph.identifiers populated post-extraction |
| Persistence is complete | Write path exists; read path exists; but nothing to write | After P0.1+P0.2, identifiers table must contain rows after ingestion |
| Repository supports identifier lookup | `search_identifiers(value)` exists but always returns [] | After P0.1+P0.2, must return matching entities; add type/page/chunk methods |
| Retrieval uses identifier index | `IDENTIFIER_LOOKUP` strategy selected but falls back to chunks | Implement `retrieve_identifiers` tool; wire to `IdentifierReader` |
| Planner recognizes identifier queries | No `IdentifierLookupTask` exists | Add task type; wire to `DocumentLookupService.search_identifiers()` |
| Hybrid retrieval uses identifier search before semantic | Currently semantic-only with keyword supplement | Identifier index query first, targeted chunk fetch second, semantic expansion third |
| Deep research can leverage identifiers | No awareness in `ResearchService` or `DeterministicResearchPlanner` | Add identifier patterns to planner; add identifier pre-fetch step to research execution |
| Answer generation receives structured identifiers | Only intent string "identifier_lookup"; no Identifier objects | Add `resolved_identifiers` field to `AnswerGenerationRequest`; update prompt |
| Unit tests exist | No tests for identifier creation path | Tests for `IdentifierPromotionService`, `DeterministicIdentifierScanner`, `retrieve_identifiers` tool |
| Integration tests exist | No end-to-end identifier test | Test: ingest document → verify identifiers table populated → query by part number → verify result |

---

## Appendix — File Reference Map

| Purpose | File |
|---|---|
| Identifier domain entity | `src/domain/document/entities/identifier.py` |
| Identifier type enum | `src/domain/common/enums.py::IdentifierType` |
| Identifier ORM | `src/infrastructure/db/orm_models/document_models.py::IdentifierORM` |
| Identifier mapper | `src/infrastructure/db/mappers/document/identifier_mapper.py::IdentifierMapper` |
| Identifier reader | `src/infrastructure/db/repositories/identifier_reader.py::IdentifierReader` |
| Document graph container | `src/domain/document/aggregates/document_graph.py::DocumentGraph.identifiers` |
| Extraction workflow | `src/application/workflows/extraction/extraction_workflow.py::ExtractionWorkflow` |
| Extraction result (no identifiers) | `src/domain/extraction/extraction_result.py::ExtractionResult` |
| Extraction prompt (misnamed) | `src/application/prompts/extraction/identifier_extraction_prompt_builder.py` |
| Query token extractor | `src/application/workflows/retrieval/retrieval_query_identifier_extractor.py` |
| Token regex source | `src/application/workflows/retrieval/deduplication/retrieved_chunk_signature.py::extract_identifier_tokens` |
| Query model | `src/domain/retrieval/retrieval_query.py::RetrievalQuery.detected_identifiers` |
| Strategy selector | `src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py` |
| SQL retrieval (identifier weights) | `src/infrastructure/db/repositories/retrieval/sql_keyword_repository.py` |
| Qdrant payload (no identifiers) | `src/infrastructure/retrieval/vector/qdrant_payload_mapper.py` |
| Identifier evidence guardrail | `src/application/guardrails/retrieval/identifier_evidence_guardrail.py` |
| Answer intent | `src/application/services/answer_generation/intent/answer_intent_analyzer.py` |
| Answer prompt | `src/application/prompts/answer_generation/answer_prompt_builder.py` |
| Document lookup service | `src/application/services/document/document_lookup_service.py` |
| Plan executor (no identifier task) | `src/application/langgraph/planning/plan_executor.py` |
| Research planner (no identifier patterns) | `src/application/langgraph/research/` |

*Created: 2026-07-01 — identifier_architecture_review.md*
