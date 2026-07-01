# Identifier Pipeline — End-to-End Verification Report

**Date:** 2026-07-01  
**Scope:** Complete lifecycle audit of every IdentifierType from ingestion through answer generation.  
**Status:** Audit only — no code changes made.

---

## 1. Identifier Inventory

### 1.1 IdentifierType Enum
`src/domain/common/enums.py`

| Value | String repr | Promoted by | Scanned by |
|---|---|---|---|
| `PART_NUMBER` | `"part_number"` | IdentifierPromotionService (SparePart.part_number) | — |
| `SERIAL_NUMBER` | `"serial_number"` | IdentifierPromotionService (EquipmentInfo.serial_number) | — |
| `MODEL_NUMBER` | `"model_number"` | IdentifierPromotionService (EquipmentInfo.model_number) | — |
| `DRAWING_NUMBER` | `"drawing_number"` | — | DeterministicIdentifierScanner (`DRG\|DWG[-\s]?\d{3,}`) |
| `COMPONENT_CODE` | `"component_code"` | — | DeterministicIdentifierScanner (`CERT\|ISO\|EN\|IEC\|ATEX\s*[-\s]?\d{3,}`) |
| `UNKNOWN` | `"unknown"` | LLM extraction fallback | — |

### 1.2 Missing Types

| Type | Root cause |
|---|---|
| `MANUFACTURER_NAME` | Manufacturer.name is stored in a separate ORM table and never promoted to Identifier |
| `SUPPLIER_NAME` | No supplier entity exists in the extraction schema |
| `CERTIFICATE_NUMBER` | Certificate patterns (ISO, IEC, ATEX) are classified as `COMPONENT_CODE` — semantic mismatch |
| `ORDER_CODE` | Mentioned in `plan_prompt_builder.py:18` hint text but absent from the IdentifierType enum |

---

## 2. End-to-End Lifecycle per Type

### PART_NUMBER
| Stage | Component | Verdict |
|---|---|---|
| Extraction | `IdentifierPromotionService` promotes `SparePart.part_number` | ✅ Covered |
| Scanning | `DeterministicIdentifierScanner` — no generic part number regex | ❌ Not scanned from chunk text |
| Persistence | `IdentifierORM` (identifiers table) | ✅ Persisted |
| Retrieval signal | `RetrievalSignalExtractor` — "part number"/"P/N" in `_IDENTIFIER_TERMS` | ✅ Triggers IDENTIFIER_LOOKUP |
| Planner detection | `DeterministicPlanner._identifier_type_from_input` maps "part number" → `part_number` | ✅ Detected |
| retrieve_identifiers arg | `identifier_type="part_number"` injected | ✅ Correct |
| Answer context | Stored under canonical key `retrieve_evidence`; no type-specific formatting | ⚠️ Generic |

### SERIAL_NUMBER
| Stage | Component | Verdict |
|---|---|---|
| Extraction | `IdentifierPromotionService` promotes `EquipmentInfo.serial_number` | ✅ Covered |
| Scanning | No regex in `DeterministicIdentifierScanner` | ❌ Not scanned from chunk text |
| Persistence | `IdentifierORM` | ✅ Persisted |
| Retrieval signal | "serial number"/"S/N" in `_IDENTIFIER_TERMS` | ✅ Triggers IDENTIFIER_LOOKUP |
| Planner detection | Maps "serial number" → `serial_number` | ✅ Detected |
| Answer context | Generic; no serial-number-specific formatting | ⚠️ Generic |

### MODEL_NUMBER
| Stage | Component | Verdict |
|---|---|---|
| Extraction | `IdentifierPromotionService` promotes `EquipmentInfo.model_number` | ✅ Covered |
| Scanning | No regex in `DeterministicIdentifierScanner` | ❌ Not scanned from chunk text |
| Persistence | `IdentifierORM` | ✅ Persisted |
| Retrieval signal | "model" in `_IDENTIFIER_TERMS` | ✅ Triggers IDENTIFIER_LOOKUP |
| Planner detection | Maps "model number" → `model_number` | ✅ Detected |
| Answer context | Generic | ⚠️ Generic |

### DRAWING_NUMBER
| Stage | Component | Verdict |
|---|---|---|
| Extraction | `DeterministicIdentifierScanner` (`_DRAWING_RE: DRG\|DWG[-\s]?\d{3,}`) | ✅ Scanned from chunks |
| Promotion | Not promoted via `IdentifierPromotionService` (no structured entity field) | — N/A |
| Persistence | `IdentifierORM` | ✅ Persisted |
| Retrieval signal | "drawing number" in `_IDENTIFIER_TERMS` | ✅ Triggers IDENTIFIER_LOOKUP |
| Planner detection | Maps "drawing" → `drawing_number` | ✅ Detected |
| Answer context | Generic | ⚠️ Generic |

### COMPONENT_CODE
| Stage | Component | Verdict |
|---|---|---|
| Extraction | `DeterministicIdentifierScanner` (`_CERT_RE: CERT\|ISO\|EN\|IEC\|ATEX\s*[-\s]?\d{3,}`) | ✅ Scanned from chunks |
| Semantic accuracy | Certificate numbers (ISO-9001, IEC-61511) classified as COMPONENT_CODE — not a dedicated CERTIFICATE_NUMBER type | ❌ Misclassified |
| Persistence | `IdentifierORM` | ✅ Persisted |
| Retrieval signal | "certificate number"/"component code" in `_IDENTIFIER_TERMS` | ✅ Triggers IDENTIFIER_LOOKUP |
| Planner detection | Maps "certificate" → `component_code` | ✅ Detected |
| Answer context | Generic | ⚠️ Generic |

### UNKNOWN
| Stage | Component | Verdict |
|---|---|---|
| Extraction | LLM extraction (`DocumentExtractionWorkflow`) assigns UNKNOWN when type cannot be classified | ✅ Covered |
| Planner detection | `DeterministicPlanner._identifier_type_from_input` returns None → no explicit type arg sent | ✅ Correct |
| retrieve_identifiers arg | No `identifier_type` arg; tool does value-only search | ✅ Works |

---

## 3. Extraction Coverage

Two distinct extraction paths. Neither covers all types.

### 3.1 IdentifierPromotionService
`src/application/services/document/identifier_promotion_service.py`

Promotes structured entity fields from `DocumentGraph` entities to `Identifier` domain objects.

| Source field | Target IdentifierType | Covered |
|---|---|---|
| `SparePart.part_number` | `PART_NUMBER` | ✅ |
| `EquipmentInfo.serial_number` | `SERIAL_NUMBER` | ✅ |
| `EquipmentInfo.model_number` | `MODEL_NUMBER` | ✅ |
| `Manufacturer.name` | `MANUFACTURER_NAME` | ❌ Not promoted — stored only in `ManufacturerORM` |
| Supplier (any field) | `SUPPLIER_NAME` | ❌ No supplier entity in extraction schema |

**Critical gap:** `Manufacturer.name` is the most queried entity in industrial documents ("who is the manufacturer of X?") but it is unreachable via `retrieve_identifiers`.

### 3.2 DeterministicIdentifierScanner
`src/application/services/document/deterministic_identifier_scanner.py`

Scans chunk text with regex patterns. Only two patterns exist:

| Pattern | Regex | IdentifierType |
|---|---|---|
| `_DRAWING_RE` | `\b(?:DRG\|DWG)[-\s]?\d{3,}\b` | `DRAWING_NUMBER` |
| `_CERT_RE` | `\b(?:CERT\|ISO\|EN\|IEC\|ATEX)\s*[-\s]?\d{3,}\b` | `COMPONENT_CODE` |

**Gaps:**
- No generic part number pattern (e.g., `HP-001`, `FLT-100`) — part numbers embedded in chunk text are never extracted
- No serial number pattern
- No model number pattern
- No manufacturer pattern

### 3.3 LLM Extraction
`src/application/services/document/document_extraction_workflow.py` (via `DocumentExtractionSchema`)

LLM extraction produces structured entities including SparePart, EquipmentInfo, Manufacturer objects. These then feed into IdentifierPromotionService. Unclassified values default to `UNKNOWN`.

---

## 4. Promotion

### 4.1 What IdentifierPromotionService Promotes
`src/application/services/document/identifier_promotion_service.py`

The service iterates `DocumentGraph.spare_parts`, `DocumentGraph.equipment`, and `DocumentGraph.manufacturers`:

```
SparePart.part_number  →  Identifier(type=PART_NUMBER)
EquipmentInfo.model_number  →  Identifier(type=MODEL_NUMBER)
EquipmentInfo.serial_number  →  Identifier(type=SERIAL_NUMBER)
Manufacturer.name  →  NOT promoted (no mapping)
```

### 4.2 DocumentGraph Structure
`src/domain/document/document_graph.py`

`DocumentGraph.identifiers` is a `dict[str, Identifier]`. Spare parts, equipment, and manufacturers are stored in separate ORM tables (`spare_parts`, `equipment_info`, `manufacturers`) — they are NOT linked to the `identifiers` table.

```
DocumentGraph:
  identifiers: dict[str, Identifier]   ← only objects that completed promotion/scanning
  spare_parts: list[SparePart]         ← separate ORM
  equipment: list[EquipmentInfo]        ← separate ORM
  manufacturers: list[Manufacturer]     ← separate ORM
```

The identifiers collection is **not** a view of spare_parts or equipment — it is a separately populated collection.

---

## 5. Persistence

### 5.1 ORM Model
`src/infrastructure/orm/identifier_orm.py`

`IdentifierORM` columns:
- `identifier_id` (PK)
- `document_id` (FK)
- `raw_value`
- `normalized_value`
- `identifier_type` (string discriminator mapped from IdentifierType enum)
- `chunk_id` (nullable — populated by scanner, not promotion)
- `section_id` (nullable)
- `page_start`, `page_end` (nullable)

### 5.2 Separate ORM Tables

| Table | ORM class | Linked to identifiers table |
|---|---|---|
| `identifiers` | `IdentifierORM` | — (this IS the identifiers table) |
| `spare_parts` | `SparePartORM` | ❌ No foreign key link |
| `equipment_info` | `EquipmentInfoORM` | ❌ No foreign key link |
| `manufacturers` | `ManufacturerORM` | ❌ No foreign key link |

There is no cross-link between `spare_parts.part_number` and `identifiers.raw_value`. Querying `retrieve_identifiers` for a part number will only find it if IdentifierPromotionService has already ingested and promoted that spare part.

### 5.3 Deduplication
`DeterministicIdentifierScanner` deduplicates by `(normalized_value, identifier_type)` during a single scan pass. Cross-ingestion deduplication depends on whether `existing_normalized` is passed (caller-controlled).

---

## 6. Retrieval

### 6.1 retrieve_identifiers Tool
`src/application/tools/retrieval/retrieve_identifiers_tool.py`

Accepts:
- `identifier_value` (str, optional) — value to search for
- `identifier_type` (str, optional) — filter by type
- `document_id` (str, optional) — scope to a document
- `query` / `query_text` (str, optional) — semantic search fallback

Queries ONLY the `identifiers` table. Does NOT query `spare_parts`, `equipment_info`, or `manufacturers`.

**Consequence:** A query for "manufacturer Grundfos" will return zero results from `retrieve_identifiers` even if Grundfos is in the manufacturers table, because Manufacturer.name is never promoted to the identifiers table.

### 6.2 Retrieval Signal Extractor
`src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py`

Signal scoring for IDENTIFIER_LOOKUP strategy:

| Signal source | Points | Covered terms |
|---|---|---|
| Pattern match (`_IDENTIFIER_VALUE_RE`) | 4.0 | `[A-Z]{1,5}-?\d{1,6}[A-Z0-9-]*` and variants |
| Detected identifier entity | 4.5 | Any identifier present in state |
| Identifier term | 3.5 | "part no", "part number", "serial number", "model", "order code", "tag", "certificate number", "drawing number", "id" |

**Gaps in `_IDENTIFIER_TERMS`:**
- `"manufacturer"` — NOT present → manufacturer queries score 0.0 for IDENTIFIER_LOOKUP
- `"supplier"` — NOT present → supplier queries score 0.0
- `"spare part"` — NOT present

### 6.3 Retrieval Plan Builder
`src/application/langgraph/retrieval_strategy/planners/retrieval_plan_builder.py:82–84`

Maps `RetrievalStrategy.IDENTIFIER_LOOKUP → "retrieve_identifiers"`. This mapping is correct.

---

## 7. Planner Coverage

All four planning gates are now open for `retrieve_identifiers`.

### 7.1 PlanPolicy
`src/application/langgraph/planning/plan_policy.py`

`"retrieve_identifiers"` is in `_DEFAULT_ALLOWED_TOOLS`. LLM-proposed plans containing this tool will not be blocked.

### 7.2 PlanValidator
`src/application/langgraph/planning/plan_validator.py`

```python
_RETRIEVAL_TOOLS = {"retrieve_chunks", "retrieve_identifiers", "retrieval_trace"}

_KNOWN_ARGS = {
    ...
    "retrieve_identifiers": {"identifier_value", "identifier_type", "document_id", "query"},
    ...
}
```

Both checks pass: tool is recognized as a retrieval tool; known args are enforced.

### 7.3 PlanRepair
`src/application/langgraph/planning/plan_repair.py`

`retrieve_identifiers` is in both:
- `_ALLOWED_ARGS` (strips unknown args from LLM-proposed plans)
- The document_id injection set (injects `selected_document_id` when a document is in scope)

### 7.4 PlanPromptBuilder
`src/application/langgraph/planning/plan_prompt_builder.py:18–25`

Hint text:
```
Search for specific identifiers such as part numbers, serial numbers, model numbers,
order codes, or drawing numbers. Args: identifier_value (str, required),
identifier_type (optional: 'part_number'|'serial_number'|'model_number'|'order_code'|'drawing_number'),
document_id (optional, to scope to a single document).
```

**Gap:** The hint lists `order_code` and `drawing_number` as `identifier_type` values but:
- `order_code` does not exist in `IdentifierType` enum
- The correct enum value for drawing numbers is `drawing_number` ✅ (correct)
- The correct enum value for component codes is `component_code` (not mentioned in hint)

### 7.5 DeterministicPlanner
`src/application/langgraph/planning/deterministic_planner.py`

Identifier detection runs before compound-plan detection in `create_plan()`.

```python
_IDENTIFIER_VALUE_RE = re.compile(
    r"\b([A-Z]{1,5}-?\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+|DN\s*\d+)\b"
)
_IDENTIFIER_TERM_RE = re.compile(
    r"\b(?:part\s*(?:number|no\.?)|p/?n\.?|serial\s*(?:number|no\.?)|s/?n\.?|"
    r"model\s*(?:number|no\.?)|order\s*code|drawing\s*(?:number|no\.?)|"
    r"tag\s*(?:number|no\.?)?|certificate\s*(?:number|no\.?)|component\s*code)\b",
    re.IGNORECASE,
)
```

Plan shape: `retrieve_identifiers → [retrieve_chunks (conditional)] → answer_question`

Type inference in `_identifier_type_from_input`:

| Keyword | Inferred identifier_type |
|---|---|
| "part number", "part no", "P/N" | `part_number` |
| "serial number", "S/N" | `serial_number` |
| "model number", "model no" | `model_number` |
| "drawing", "DRG", "DWG" | `drawing_number` |
| "certificate", "tag" | `component_code` |
| None matched | None (no `identifier_type` arg) |

Diagnostics always include `identifier_value` and `plan_kind="identifier_lookup"`.

---

## 8. Deep Research Coverage

### 8.1 ResearchPlanningPromptBuilder
`src/application/langgraph/research/prompts/research_planning_prompt_builder.py`

Upgraded from a bare comma-separated strategy list to per-strategy descriptions with explicit when-to-use guidance:

```
IDENTIFIER_LOOKUP: Use when the question references a specific identifier such as a part number,
  serial number, model number, order code, drawing number, or tag number (e.g. 'HP-001', 'SN-2024').
  Frame the task question as: 'What evidence describes identifier [value]?'
```

The schema example now demonstrates an identifier task. All 11 strategies have descriptions.

### 8.2 DeterministicResearchPlanner
`src/application/langgraph/research/planners/deterministic_research_planner.py`

`_task_for_concept()` now extracts `identifier_value` into `diagnostics` when `strategy == IDENTIFIER_LOOKUP`:

```python
if strategy == RetrievalStrategy.IDENTIFIER_LOOKUP:
    identifier_value = self._extract_identifier_value(concept)
    if identifier_value:
        diagnostics["identifier_value"] = identifier_value
```

This surfaces the detected value in the research task trace.

### 8.3 Research-to-Retrieval Bridge
`src/application/langgraph/retrieval_strategy/planners/retrieval_plan_builder.py:82–84`

`IDENTIFIER_LOOKUP → retrieve_identifiers` mapping is in place. The research planner's strategy choice flows through to the correct tool.

### 8.4 Deep Research Gap
The research path inherits the same signal extractor gap:
- `RetrievalSignalExtractor` will not select `IDENTIFIER_LOOKUP` for queries containing only "manufacturer", "supplier", or "spare part"
- The LLM research planner may select it based on prompt guidance, but the deterministic research planner will not

---

## 9. Answer Generation Context

### 9.1 Canonical Key Aliasing
`src/application/langgraph/planning/plan_executor.py:279–283`

```python
canonical_key = {
    "retrieve_chunks": "retrieve_evidence",
    "retrieve_identifiers": "retrieve_evidence",
}.get(tool_name, tool_name)
tool_results[canonical_key] = serialized
```

Both `retrieve_chunks` and `retrieve_identifiers` results are stored under the single canonical key `"retrieve_evidence"`. When a plan runs `retrieve_identifiers → retrieve_chunks → answer_question`, the `retrieve_chunks` result overwrites the `retrieve_identifiers` result under this key.

**Consequence:** In a compound plan (retrieve_identifiers + retrieve_chunks), only the chunks result survives in `tool_results["retrieve_evidence"]`. The identifier result is still in `tool_results[step.output_key]` (the step-specific key) and in `step_outputs`, but the canonical view is overwritten.

### 9.2 answer_question Node Context
`src/application/langgraph/nodes/question_answering/answer_question_node.py`

The `answer_question` node calls its tool with `AnswerQuestionRequest`. It does not have special handling for identifier-typed results. Identifier data reaches the LLM answer model as part of the serialized `retrieve_evidence` context blob — there is no identifier-specific context rendering or citation format.

### 9.3 What the LLM Receives
The LLM sees identifier results as generic evidence text. The `Identifier` domain object fields (`raw_value`, `normalized_value`, `identifier_type`, `chunk_id`, `page_start`, `page_end`) are serialized into the context, but no template surfaces them in a structured way (e.g., "Identifier HP-001 [PART_NUMBER] found on page 12").

---

## 10. Gap Analysis

| # | Gap | File / Location | Severity |
|---|---|---|---|
| G-01 | `Manufacturer.name` never promoted to Identifier — unreachable via `retrieve_identifiers` | `identifier_promotion_service.py` | **High** |
| G-02 | `"manufacturer"` / `"supplier"` absent from `_IDENTIFIER_TERMS` — IDENTIFIER_LOOKUP never selected for manufacturer queries | `retrieval_signal_extractor.py` | **High** |
| G-03 | No generic part number regex in `DeterministicIdentifierScanner` — part numbers embedded in chunk text are never extracted | `deterministic_identifier_scanner.py` | **High** |
| G-04 | `order_code` in plan_prompt_builder hint does not exist in `IdentifierType` enum — LLM may propose invalid `identifier_type` values | `plan_prompt_builder.py:21` | **Medium** |
| G-05 | Certificate numbers (ISO-9001, IEC-61511) classified as `COMPONENT_CODE` — no distinct `CERTIFICATE_NUMBER` type | `deterministic_identifier_scanner.py` + `IdentifierType` enum | **Medium** |
| G-06 | In compound plans (retrieve_identifiers + retrieve_chunks), the identifier result is overwritten in `tool_results["retrieve_evidence"]` by the chunks result | `plan_executor.py:281` | **Medium** |
| G-07 | No identifier-specific context rendering in answer generation — identifiers and chunks are indistinguishable to the answer LLM | `answer_question_node.py` | **Low** |
| G-08 | `Supplier` entity absent from extraction schema entirely — no promotion path exists | `DocumentExtractionSchema` | **Low** |
| G-09 | No serial number or model number regex in `DeterministicIdentifierScanner` — these types only reachable via structured entity promotion | `deterministic_identifier_scanner.py` | **Low** |

---

## 11. Recommended Improvements

All recommendations preserve DDD, Clean Architecture, Repository pattern, and existing folder structure.

### R-01 (High) — Promote Manufacturer.name to MANUFACTURER_NAME
Add `MANUFACTURER_NAME = "manufacturer_name"` to `IdentifierType` enum. Add a promotion loop in `IdentifierPromotionService` that iterates `document_graph.manufacturers` and creates `Identifier(type=MANUFACTURER_NAME, raw_value=m.name)`. No schema or ORM changes required.

### R-02 (High) — Add manufacturer/supplier to _IDENTIFIER_TERMS
In `retrieval_signal_extractor.py`, add `"manufacturer"`, `"supplier"`, `"made by"`, `"manufactured by"` to `_IDENTIFIER_TERMS`. This will allow manufacturer queries to route to `IDENTIFIER_LOOKUP` in both the question-answering and deep research paths.

### R-03 (High) — Add generic part number pattern to DeterministicIdentifierScanner
Add a third regex entry to `_PATTERNS` in `deterministic_identifier_scanner.py`:
```python
_GENERIC_ID_RE = re.compile(r"\b[A-Z]{1,5}-?\d{1,6}[A-Z0-9-]*\b")
```
mapped to `IdentifierType.PART_NUMBER`. Apply only when not already matched by DRAWING or CERT patterns to avoid double-classification.

### R-04 (Medium) — Fix plan_prompt_builder identifier_type hint
In `plan_prompt_builder.py:21`, replace `'order_code'` with `'component_code'` and add `'component_code'` to the listed values. Remove `'order_code'` entirely since it doesn't exist in the enum.

### R-05 (Medium) — Resolve canonical key collision in compound plans
In `plan_executor.py:279`, change the canonical key mapping so `retrieve_identifiers` uses a distinct canonical key `"retrieve_identifiers"` rather than sharing `"retrieve_evidence"` with `retrieve_chunks`. Update the `answer_question` node or the context builder to merge both keys into the answer context.

### R-06 (Medium) — Consider CERTIFICATE_NUMBER type
If domain semantics require distinguishing between equipment component codes and compliance certificates, add `CERTIFICATE_NUMBER = "certificate_number"` to `IdentifierType` and update `_CERT_RE` mapping in `DeterministicIdentifierScanner` accordingly.

---

## 12. Acceptance Checklist

| Identifier Type | Extracted | Promoted/Scanned | Persisted | Retrieval Signal | Planner Detects | Deep Research Hint | Answer Context |
|---|---|---|---|---|---|---|---|
| PART_NUMBER | ✅ (structured entity) | ✅ (promotion) | ✅ | ✅ ("part number") | ✅ | ✅ | ⚠️ generic |
| SERIAL_NUMBER | ✅ (structured entity) | ✅ (promotion) | ✅ | ✅ ("serial number") | ✅ | ✅ | ⚠️ generic |
| MODEL_NUMBER | ✅ (structured entity) | ✅ (promotion) | ✅ | ✅ ("model") | ✅ | ✅ | ⚠️ generic |
| DRAWING_NUMBER | ✅ (chunk scan) | ✅ (scanner) | ✅ | ✅ ("drawing number") | ✅ | ✅ | ⚠️ generic |
| COMPONENT_CODE | ✅ (chunk scan — CERT/ISO/IEC) | ✅ (scanner) | ✅ | ✅ ("certificate number") | ✅ | ✅ | ⚠️ generic |
| MANUFACTURER_NAME | ❌ not promoted | ❌ | ❌ not in identifiers table | ❌ no signal | ❌ | ❌ | ❌ |
| ORDER_CODE (hint only) | ❌ no type exists | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| CERTIFICATE_NUMBER (distinct) | ❌ mapped to COMPONENT_CODE | ❌ | ❌ | ⚠️ partial ("certificate number") | ❌ | ❌ | ❌ |

### Test Coverage Checklist

| Component | Tests | Status |
|---|---|---|
| PlanPolicy allows retrieve_identifiers | `test_plan_policy.py::test_plan_policy_default_allows_retrieve_identifiers` | ✅ |
| PlanValidator accepts retrieve_identifiers step | `test_plan_validator.py::test_plan_validator_accepts_retrieve_identifiers_step` | ✅ |
| PlanValidator rejects unknown args | `test_plan_validator.py::test_plan_validator_rejects_retrieve_identifiers_with_unknown_args` | ✅ |
| PlanRepair strips unknown args | `test_plan_repair.py::test_plan_repair_preserves_retrieve_identifiers_known_args` | ✅ |
| PlanRepair injects document_id | `test_plan_repair.py::test_plan_repair_injects_document_id_into_retrieve_identifiers` | ✅ |
| PlanPromptBuilder includes hint | `test_plan_prompt_builder.py::test_plan_prompt_builder_includes_retrieve_identifiers_hint` | ✅ |
| DeterministicPlanner PART_NUMBER | `test_deterministic_planner.py::test_planner_creates_identifier_lookup_plan_for_part_number` | ✅ |
| DeterministicPlanner SERIAL_NUMBER | `test_deterministic_planner.py::test_planner_identifier_plan_infers_serial_number_type` | ✅ |
| DeterministicPlanner diagnostics | `test_deterministic_planner.py::test_planner_identifier_plan_captures_identifier_value_in_diagnostics` | ✅ |
| DeterministicPlanner + PlanValidator integration | `test_deterministic_planner.py::test_plan_validator_accepts_deterministic_identifier_plan` | ✅ |
| MANUFACTURER_NAME extraction | — | ❌ Not covered |
| Manufacturer retrieval via retrieve_identifiers | — | ❌ Not covered |
| Canonical key collision (compound plan) | — | ❌ Not tested |
| RetrievalSignalExtractor manufacturer signal | — | ❌ Not covered |
