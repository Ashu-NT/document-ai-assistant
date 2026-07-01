# Planner Architecture Review
**Status:** Pre-implementation audit — no code has been changed.  
**Date:** 2026-07-01  
**Scope:** All three planning subsystems: QA/Task compound planner, Retrieval strategy selector, Research planner.

---

## 1. Executive Summary

The planning system is **genuinely hybrid**. Every subsystem runs a deterministic path unconditionally; an LLM advisory path is optional, flag-gated, schema-validated, and can never win unless the validator accepts its proposal. No LLM output reaches the executor without passing through a whitelist-based `PlanValidator`.

However, there are **four critical gaps** that prevent identifier queries from working end-to-end:

| Gap | Severity | Impact |
|-----|----------|--------|
| `retrieve_identifiers` absent from `PlanPolicy.allowed_tools` | Critical | LLM plans with this tool are always rejected |
| `retrieve_identifiers` absent from `PlanValidator._KNOWN_ARGS` | Critical | Even repaired plans fail arg validation |
| `DeterministicPlanner` has no identifier compound plan type | High | Identifier queries fall through to bare `answer_question` |
| Research planner has no `ResolveIdentifierTask` or pre-fetch step | High | Identifier-triggered research never resolves actual values before semantic search |

The retrieval strategy layer (`IDENTIFIER_LOOKUP` → `retrieve_identifiers`) is correctly wired in `RetrievalStrategyService`, `DeterministicStrategySelector`, and `RetrievalPlanBuilder`. The tool exists and the executor handles it. The problem is entirely in the task-planning layer above it.

---

## 2. Current Planning Components

### 2a. QA / Task Compound Planner

| Component | File | Class | Role |
|-----------|------|-------|------|
| Orchestrator node | `src/application/langgraph/nodes/planning/create_plan_node.py` | `CreatePlanNode` | Runs deterministic first, then optional LLM; decides which plan wins |
| Executor node | `src/application/langgraph/nodes/planning/execute_plan_node.py` | `ExecutePlanNode` | Reconstructs `ExecutionPlan`, calls `PlanExecutor` |
| Deterministic planner | `src/application/langgraph/planning/deterministic_planner.py` | `DeterministicPlanner` | Rule-based compound plan creation; handles `list_and_find`, `compare`, `explore_and_answer`, `retrieve_and_answer` |
| LLM proposer | `src/application/langgraph/planning/llm_plan_proposer.py` | `LLMPlanProposer` | Builds prompt, calls LLM, returns raw text; does NOT call tools directly |
| Plan parser | `src/application/langgraph/planning/plan_parser.py` | `PlanParser` | Strips code fences, JSON-decodes LLM output, builds `ExecutionPlan` with `source="llm"` |
| Plan validator | `src/application/langgraph/planning/plan_validator.py` | `PlanValidator` | Whitelist enforcement; rejects any step with tool not in `allowed_tools` |
| Plan repair | `src/application/langgraph/planning/plan_repair.py` | `PlanRepair` | Renames known aliases, removes blocked tools, strips unknown args; not a bypass |
| Plan policy | `src/application/langgraph/planning/plan_policy.py` | `PlanPolicy` | Holds `allowed_tools` set; source of truth for whitelist |
| Plan prompt builder | `src/application/langgraph/planning/plan_prompt_builder.py` | `PlanPromptBuilder` | Builds structured prompt with tool hints; version `v1` |
| Execution plan | `src/application/langgraph/planning/execution_plan.py` | `ExecutionPlan` | Frozen dataclass: `plan_id`, `goal`, `steps`, `source` (`deterministic`/`llm`/`repaired`) |
| Plan step | `src/application/langgraph/planning/plan_step.py` | `PlanStep` | Frozen dataclass per step: `step_id`, `tool_name`, `args`, `depends_on` |
| Plan executor | `src/application/langgraph/planning/plan_executor.py` | `PlanExecutor` | Iterates steps, calls guardrails, dispatches tools via `_build_request()` |

### 2b. Retrieval Strategy Selector

| Component | File | Class | Role |
|-----------|------|-------|------|
| Service | `src/application/langgraph/retrieval_strategy/services/retrieval_strategy_service.py` | `RetrievalStrategyService` | Full pipeline: signals → selector → advisor → validator → builder → plan validator |
| Signal extractor | `src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py` | `RetrievalSignalExtractor` | Pattern + term scoring; identifier pattern = 4.0 pts, identifier term = 3.5 pts |
| Deterministic selector | `src/application/langgraph/retrieval_strategy/selectors/deterministic_strategy_selector.py` | `DeterministicStrategySelector` | `"identifier"` signal → `IDENTIFIER_LOOKUP`; threshold ≥ 4.0 = strong |
| Strategy advisor | `src/application/langgraph/strategy_advisor/advisor.py` | `StrategyAdvisor` | Optional LLM advisory; only triggered on low confidence / complex intents |
| Plan builder | `src/application/langgraph/retrieval_strategy/planners/retrieval_plan_builder.py` | `RetrievalPlanBuilder` | `IDENTIFIER_LOOKUP` → tool `"retrieve_identifiers"`; falls back to `retrieve_chunks` if not in registry |
| Plan executor | `src/application/langgraph/retrieval_strategy/executors/retrieval_plan_executor.py` | `RetrievalPlanExecutor` | Handles `retrieve_identifiers` → `RetrieveIdentifiersRequest` |

### 2c. Research Planner

| Component | File | Class | Role |
|-----------|------|-------|------|
| Orchestrator node | `src/application/langgraph/nodes/research/create_research_plan_node.py` | `CreateResearchPlanNode` | Calls `research_service.plan_research()` with `use_llm_planner` flag |
| Deterministic planner | `src/application/langgraph/research/planners/deterministic_research_planner.py` | `DeterministicResearchPlanner` | `_CATEGORY_PATTERNS` includes identifier pattern; maps to `IDENTIFIER_LOOKUP` strategy hint via `_strategy_for_concept()` |
| LLM planner | `src/application/langgraph/research/planners/llm_research_planner.py` | `LLMResearchPlanner` | Calls LLM, parses JSON, builds tasks via `ResearchPlanBuilder`; tasks have `strategy_hint` but no `identifier_value` field |

---

## 3. Current Planning Flow

### 3a. QA / Task Compound Planner Flow

```
User Input
    │
    ▼
IntentRouter.route()
    │  RouteType.PLANNED_TASK / ANSWER_QUESTION / DEEP_RESEARCH
    ▼
CreatePlanNode.__call__()
    │
    ├─[Always]──► DeterministicPlanner.create_plan(state)
    │               │  Checks compound markers: "compare", " and ", "retrieve evidence ... and"
    │               │  Plan types: list_and_find, compare, explore_and_answer, retrieve_and_answer
    │               │  Returns ExecutionPlan(source="deterministic") or None
    │
    ├─[If deterministic plan exists AND (LLM disabled OR confidence ≥ 0.8)]
    │   └──► USE deterministic plan  ──► ExecutePlanNode
    │
    └─[If llm_planning_enabled AND proposer wired]
        │
        ├──► LLMPlanProposer.propose(state)   (text output only; no tool calls)
        │         │  PlanPromptBuilder builds prompt with allowed tools + schema example
        │         ▼
        │    PlanParser.parse(raw_text)
        │         │  JSON decode → ExecutionPlan(source="llm")
        │         ▼
        │    PlanValidator.validate(plan, policy)
        │         │  Checks: max_steps, duplicate step_ids, blocked tools,
        │         │           allowed_tools whitelist, _KNOWN_ARGS, dependencies,
        │         │           document scope, mutating tool
        │         │
        │    [If invalid]──► PlanRepair.repair(plan, policy)
        │         │              Renames aliases, removes blocked tools, strips unknown args
        │         │          PlanValidator.validate() again
        │         │
        │    [If still invalid AND deterministic plan exists]
        │         └──► USE deterministic plan with warning
        │
        │    [If LLM plan valid]──► ExecutePlanNode
        │
        └─[If no plan at all]──► route to answer_question (bare, no planning)

ExecutePlanNode
    │
    ▼
ExecutionPlan.from_dict(raw_plan)
    │
    ▼
PlanExecutor.execute(plan, state)
    │  For each step in topological order:
    │    1. GuardrailService.check(step)
    │    2. _build_request(step) → dispatch to tool handler
    │       Handled tools: list_documents, find_document, document_details,
    │                      explore_document, retrieve_chunks, retrieve_identifiers,
    │                      answer_question, run_quality_gate, retrieval_trace
    │    3. _store_canonical_tool_result(step, result)
    ▼
  State updated with results
```

### 3b. Retrieval Strategy Selector Flow

```
Query
    │
    ▼
RetrievalSignalExtractor.extract()
    │  Scores signals: identifier pattern=4.0, identifier term=3.5, semantic=2.0...
    ▼
DeterministicStrategySelector.select()
    │  score ≥ 4.0 → strong signal → IDENTIFIER_LOOKUP
    │  score < 4.0 → SEMANTIC_SEARCH or HYBRID
    │
    ├─[If policy.llm_strategy_enabled AND context.use_llm_selector AND advisor wired]
    │   └──► StrategyAdvisor.advise()
    │              │  Triggers on: deep_research, low confidence (<0.8), compare/contrast, multi-intent
    │              ▼
    │         StrategyAdvisorValidator.validate()  (schema check)
    │              │  Returns StrategyAdvisorOutcome; merged with deterministic result
    │
    ▼
RetrievalPlanBuilder.build()
    │  IDENTIFIER_LOOKUP → tool "retrieve_identifiers" (if in tool registry, else "retrieve_chunks")
    │
    ▼
PlanValidator.validate()  (strategy-level validation)
    │
    ▼
RetrievalPlanExecutor._build_request()
    │  "retrieve_identifiers" → RetrieveIdentifiersRequest
    ▼
  Retrieval results
```

### 3c. Research Planner Flow

```
Research query
    │
    ▼
DeterministicResearchPlanner.plan()
    │  _CATEGORY_PATTERNS: identifier pattern matched
    │  _strategy_for_concept(): IDENTIFIER_LOOKUP strategy_hint assigned
    │  Builds ResearchTask objects (no identifier_value field; no pre-fetch)
    │
    ├─[If use_llm_planner AND LLM planner wired]
    │   └──► LLMResearchPlanner.plan()
    │              Calls LLM → parses JSON → ResearchPlanBuilder.build_task()
    │              Tasks have strategy_hint but no identifier_value field
    │
    ▼
ResearchTask list
    │  (Each task has strategy_hint=IDENTIFIER_LOOKUP but no pre-fetched value)
    ▼
Research executor: runs semantic retrieval using strategy hint
    (No identifier value lookup precedes the semantic search)
```

---

## 4. LLM Planning Details

### LLM Plan Proposer (`LLMPlanProposer`)
- **File:** `src/application/langgraph/planning/llm_plan_proposer.py`
- **Method:** `propose(state) -> str`  
- **Behavior:** Builds a structured prompt via `PlanPromptBuilder`, calls the LLM, and returns raw text. It does **not** call any tools directly. It has no awareness of which tools are allowed; that check happens downstream.

### Prompt Construction (`PlanPromptBuilder`)
- **File:** `src/application/langgraph/planning/plan_prompt_builder.py`
- **Version:** `PLANNING_PROMPT_VERSION = "v1"`
- **`_TOOL_HINTS` current contents:** `list_documents`, `find_document`, `document_details`, `explore_document`, `retrieve_chunks`, `answer_question`, `run_quality_gate`, `retrieval_trace`
- **Missing:** `retrieve_identifiers` is not in `_TOOL_HINTS` — the LLM never learns it is available

### LLM Plan Validation (`PlanValidator`)
- **File:** `src/application/langgraph/planning/plan_validator.py`
- **`_KNOWN_ARGS` entries:** All tools except `retrieve_identifiers` — any step with `retrieve_identifiers` that passes whitelist check will fail arg validation with "unknown args"
- **`_SCOPED_TOOLS`:** `{"answer_question", "explore_document", "document_details"}`
- **`_RETRIEVAL_TOOLS`:** `{"retrieve_chunks", "retrieval_trace"}` — `retrieve_identifiers` excluded

### LLM Plan Repair (`PlanRepair`)
- **File:** `src/application/langgraph/planning/plan_repair.py`
- **`_ALLOWED_ARGS`:** Does not include `retrieve_identifiers`
- **`_TOOL_NAME_RENAMES`:** `{"retrieve_evidence": "retrieve_chunks", "ask_question": "answer_question"}` — no identifier aliases
- **Repair behavior:** Removes steps whose tool is not in policy.allowed_tools; strips unknown args. Repair cannot add `retrieve_identifiers` if the policy doesn't allow it.

### Security Guarantees (Confirmed)
- LLM output is text-only; it never directly invokes tools
- Parse → Validate → (optionally Repair → Re-validate) is mandatory before any LLM plan executes
- If validation fails after repair, the deterministic plan is used (if one exists) or planning fails safely
- `PlanValidator` is the non-bypassable security gate

---

## 5. Deterministic Planning Details

### DeterministicPlanner
- **File:** `src/application/langgraph/planning/deterministic_planner.py`
- **Method:** `create_plan(state) -> ExecutionPlan | None`

**Current plan types:**

| Plan Type | Trigger Condition | Steps Generated |
|-----------|-------------------|-----------------|
| `list_and_find` | `"show documents ... find"` or `"list documents ... open document"` | `list_documents` → `find_document` |
| `compare` | `"compare ... and ..."` | `explore_document` (×2) → `answer_question` |
| `explore_and_answer` | `"explore ... and {follow_up_marker}"` | `explore_document` → `answer_question` |
| `retrieve_and_answer` | `"retrieve evidence ... and {follow_up_marker}"` | `retrieve_chunks` → `answer_question` |

**Missing identifier plan type:** There is no `resolve_identifier`, `identifier_lookup`, or similar pattern. Queries like "find part number HP-001" or "what documents mention serial number SN-2024" receive no deterministic plan and fall through to `answer_question` directly.

### Confidence Threshold
- **`deterministic_confidence_threshold = 0.8`** in `CreatePlanNode`
- If deterministic plan confidence ≥ 0.8 AND LLM is enabled, the deterministic plan still wins
- LLM planning only activates when deterministic confidence < 0.8 or no deterministic plan exists

---

## 6. Hybrid Behavior Explanation

The system is hybrid in three independent layers:

### Layer 1: Task Planner (CreatePlanNode)
```
Deterministic (always runs) → LLM optional (flag-gated, confidence-gated)
Winner: deterministic if confidence ≥ 0.8; LLM only if deterministic fails or confidence < 0.8
Safety gate: PlanValidator (whitelist); PlanRepair is a soft fixer, not a bypass
```

### Layer 2: Retrieval Strategy Selector (RetrievalStrategyService)
```
DeterministicStrategySelector (always runs) → StrategyAdvisor optional (flag-gated, trigger-gated)
Winner: merged; deterministic strategy is the default, advisor can override if validated
Safety gate: StrategyAdvisorValidator (schema); strategy-level PlanValidator
```

### Layer 3: Research Planner (CreateResearchPlanNode)
```
DeterministicResearchPlanner (always runs) → LLMResearchPlanner optional (flag-gated)
Winner: LLM replaces deterministic if flag set and LLM succeeds
Safety gate: schema validation on LLM tasks; no explicit research-plan whitelist currently
```

### The Fundamental Invariant
**No LLM output ever reaches a tool executor without passing through schema validation and/or a tool whitelist.** This invariant is upheld across all three layers. The upgrade must preserve this property.

---

## 7. Identifier Planning Gap Analysis

Cross-referenced with `outputs/architecture/identifier_architecture_review.md`.

### Gap 1: `retrieve_identifiers` not in `PlanPolicy.allowed_tools`

**Location:** `src/application/langgraph/planning/plan_policy.py`

```python
_DEFAULT_ALLOWED_TOOLS = (
    "list_documents", "find_document", "document_details",
    "explore_document", "retrieve_chunks", "answer_question",
    "run_quality_gate", "retrieval_trace",
    # "retrieve_identifiers"  ← MISSING
)
```

**Effect:** Any LLM-proposed plan that includes `retrieve_identifiers` will be rejected by `PlanValidator.validate()` at the `allowed_tools` whitelist check. The tool exists in the executor but is unreachable from LLM plans.

### Gap 2: `retrieve_identifiers` not in `PlanValidator._KNOWN_ARGS`

**Location:** `src/application/langgraph/planning/plan_validator.py`

**Effect:** Even if `PlanPolicy` is fixed, the validator will raise "unknown args" for any `retrieve_identifiers` step because no known arg schema is registered. Steps with `identifier_value` or `identifier_type` args will be stripped/rejected.

### Gap 3: `retrieve_identifiers` not in `PlanRepair._ALLOWED_ARGS`

**Location:** `src/application/langgraph/planning/plan_repair.py`

**Effect:** During repair, all args for `retrieve_identifiers` will be stripped. A repaired plan with `retrieve_identifiers` will have no args, causing executor failure.

### Gap 4: `retrieve_identifiers` not in `PlanPromptBuilder._TOOL_HINTS`

**Location:** `src/application/langgraph/planning/plan_prompt_builder.py`

**Effect:** The LLM never learns `retrieve_identifiers` is available. Even if gaps 1-3 are fixed, the LLM will not propose it without a hint.

### Gap 5: `DeterministicPlanner` has no identifier compound plan type

**Location:** `src/application/langgraph/planning/deterministic_planner.py`

**Effect:** Queries like "what is part number HP-001" or "find all documents with serial SN-2024" receive no deterministic plan. They fall through to bare `answer_question`. The system has zero structured identifier lookup in the task planning layer.

### Gap 6: Research planner — no `ResolveIdentifierTask`, no pre-fetch step

**Location:**  
- `src/application/langgraph/research/planners/deterministic_research_planner.py`
- `src/application/langgraph/research/planners/llm_research_planner.py`

**Effect:** Identifier-categorized research concepts get `strategy_hint=IDENTIFIER_LOOKUP` but:
- There is no pre-fetch step that resolves the identifier value from the database before semantic search
- `ResearchTask` has no `identifier_value` field
- Semantic search with just the concept string (e.g., "HP-001") loses precision that a direct identifier lookup would provide

### Gap 7: `_RETRIEVAL_TOOLS` missing `retrieve_identifiers` in `PlanValidator`

**Location:** `src/application/langgraph/planning/plan_validator.py`

```python
_RETRIEVAL_TOOLS = {"retrieve_chunks", "retrieval_trace"}
# Missing: "retrieve_identifiers"
```

**Effect:** `retrieve_identifiers` is not treated as a retrieval tool for dependency-chain validation. Plans that chain identifier retrieval → answer will fail dependency checks.

---

## 8. Required Upgrade Design

### Design Mandate (Non-Negotiable Rules)

1. **No LLM direct tool execution** — LLM output is always text; tools are called by the executor only
2. **No arbitrary LLM tool names** — All tool names must appear in `PlanPolicy.allowed_tools`
3. **No guardrail bypass** — `PlanValidator` must run on every LLM-proposed plan; repair is not a bypass
4. **No free-form LLM plans** — All LLM plans must be schema-validated via `PlanParser` + `PlanValidator`
5. **Allowed task types must be whitelisted** — `PlanPolicy` is the sole source of truth

### Target Architecture: Plan Flow

```
User Input (identifier query)
    │
    ▼
DeterministicPlanner.create_plan()
    │  NEW: detect identifier patterns → create identifier_lookup plan
    │    Steps: [retrieve_identifiers] → [answer_question]
    │    OR: [retrieve_identifiers] → [retrieve_chunks] → [answer_question]  (hybrid)
    │
    [confidence ≥ 0.8] → USE deterministic plan directly
    │
    [LLM path, if enabled]
    │    LLMPlanProposer → PlanParser → PlanValidator (retrieve_identifiers NOW ALLOWED)
    │    PlanRepair (retrieve_identifiers args NOW KNOWN) → re-validate
    │
    ▼
PlanExecutor (retrieve_identifiers already handled in _build_request)
```

### New Task Types Required

#### 1. `ResolveIdentifierTask`
**Purpose:** Look up a specific identifier value across all documents.  
**Maps to tool:** `retrieve_identifiers`  
**DeterministicPlanner trigger:** Query contains identifier pattern (e.g. `HP-001`, `SN-2024`) AND no document is selected  
**Required args:** `identifier_value: str`, `identifier_type: str | None`

#### 2. `RetrieveIdentifierContextTask`
**Purpose:** Retrieve the chunk context surrounding a known identifier.  
**Maps to tool:** `retrieve_chunks` with identifier-enriched query  
**DeterministicPlanner trigger:** Follows `ResolveIdentifierTask`; uses resolved chunk_ids  
**Required args:** `query: str`, `chunk_ids: list[str] | None`

#### 3. `RetrieveIdentifierLinkedChunksTask`
**Purpose:** Retrieve chunks semantically linked to a resolved identifier.  
**Maps to tool:** `retrieve_chunks` with `strategy_hint=identifier_lookup`  
**DeterministicPlanner trigger:** Query asks for context/details about a known identifier  
**Required args:** `query: str`, `identifier_value: str`

#### 4. `RetrieveIdentifierRelatedMaintenanceTask`
**Purpose:** Retrieve maintenance tasks that reference a specific identifier.  
**Maps to tool:** `retrieve_chunks` filtered by chunk type `MAINTENANCE_PROCEDURE`  
**DeterministicPlanner trigger:** Query references "maintenance" and contains identifier pattern  
**Required args:** `query: str`, `identifier_value: str`

#### 5. `RetrieveIdentifierRelatedSpecificationsTask`
**Purpose:** Retrieve specifications that reference a specific identifier.  
**Maps to tool:** `retrieve_chunks` filtered by chunk type `TECHNICAL_SPECIFICATION`  
**DeterministicPlanner trigger:** Query references "specification" or "spec" and contains identifier pattern  
**Required args:** `query: str`, `identifier_value: str`

#### 6. `CompareIdentifierReferencesTask`
**Purpose:** Compare how a specific identifier is used across multiple documents.  
**Maps to tool:** `retrieve_identifiers` (×N documents) then `answer_question`  
**DeterministicPlanner trigger:** Query contains "compare" and identifier pattern  
**Required args:** `identifier_value: str`, `document_ids: list[str] | None`

### Example Plans

#### Example 1: Single identifier lookup (no document selected)
```json
{
  "plan_id": "plan_001",
  "goal": "Find part number HP-001 across all documents",
  "source": "deterministic",
  "steps": [
    {
      "step_id": "s1",
      "tool_name": "retrieve_identifiers",
      "args": {"identifier_value": "HP-001", "identifier_type": "part_number"},
      "output_key": "identifier_results"
    },
    {
      "step_id": "s2",
      "tool_name": "answer_question",
      "args": {"question": "What documents contain part number HP-001 and what is its context?"},
      "depends_on": ["s1"],
      "input_key": "identifier_results"
    }
  ]
}
```

#### Example 2: Identifier context in selected document
```json
{
  "plan_id": "plan_002",
  "goal": "Retrieve context for serial number SN-2024-001 in the current document",
  "source": "deterministic",
  "steps": [
    {
      "step_id": "s1",
      "tool_name": "retrieve_identifiers",
      "args": {"identifier_value": "SN-2024-001", "document_id": "doc_abc"},
      "output_key": "identifier_hits"
    },
    {
      "step_id": "s2",
      "tool_name": "retrieve_chunks",
      "args": {"query": "SN-2024-001 serial number context usage", "document_id": "doc_abc"},
      "depends_on": ["s1"],
      "output_key": "context_chunks"
    },
    {
      "step_id": "s3",
      "tool_name": "answer_question",
      "args": {"question": "What is the usage and context for serial number SN-2024-001?"},
      "depends_on": ["s2"],
      "input_key": "context_chunks"
    }
  ]
}
```

#### Example 3: Maintenance tasks referencing a part number
```json
{
  "plan_id": "plan_003",
  "goal": "Find all maintenance tasks that reference HP-001",
  "source": "deterministic",
  "steps": [
    {
      "step_id": "s1",
      "tool_name": "retrieve_identifiers",
      "args": {"identifier_value": "HP-001"},
      "output_key": "identifier_hits"
    },
    {
      "step_id": "s2",
      "tool_name": "retrieve_chunks",
      "args": {
        "query": "HP-001 maintenance replacement procedure",
        "chunk_types": ["maintenance_procedure"]
      },
      "depends_on": ["s1"],
      "output_key": "maintenance_chunks"
    },
    {
      "step_id": "s3",
      "tool_name": "answer_question",
      "args": {"question": "What maintenance tasks reference part number HP-001?"},
      "depends_on": ["s2"],
      "input_key": "maintenance_chunks"
    }
  ]
}
```

#### Example 4: Cross-document identifier comparison
```json
{
  "plan_id": "plan_004",
  "goal": "Compare how model HP-500 is referenced across documents",
  "source": "deterministic",
  "steps": [
    {
      "step_id": "s1",
      "tool_name": "retrieve_identifiers",
      "args": {"identifier_value": "HP-500"},
      "output_key": "identifier_hits"
    },
    {
      "step_id": "s2",
      "tool_name": "retrieve_chunks",
      "args": {"query": "HP-500 model specifications comparison"},
      "depends_on": ["s1"],
      "output_key": "spec_chunks"
    },
    {
      "step_id": "s3",
      "tool_name": "answer_question",
      "args": {"question": "How does HP-500 differ across the documents?"},
      "depends_on": ["s2"],
      "input_key": "spec_chunks"
    }
  ]
}
```

#### Example 5: Identifier specifications lookup
```json
{
  "plan_id": "plan_005",
  "goal": "Retrieve technical specifications for part number FLT-100",
  "source": "deterministic",
  "steps": [
    {
      "step_id": "s1",
      "tool_name": "retrieve_identifiers",
      "args": {"identifier_value": "FLT-100", "identifier_type": "part_number"},
      "output_key": "identifier_hits"
    },
    {
      "step_id": "s2",
      "tool_name": "retrieve_chunks",
      "args": {
        "query": "FLT-100 filter technical specification dimensions rating",
        "chunk_types": ["technical_specification"]
      },
      "depends_on": ["s1"],
      "output_key": "spec_chunks"
    },
    {
      "step_id": "s3",
      "tool_name": "answer_question",
      "args": {"question": "What are the technical specifications for part FLT-100?"},
      "depends_on": ["s2"],
      "input_key": "spec_chunks"
    }
  ]
}
```

### Validator Updates Required

**`PlanPolicy._DEFAULT_ALLOWED_TOOLS` — add:**
```python
"retrieve_identifiers"
```

**`PlanValidator._KNOWN_ARGS` — add:**
```python
"retrieve_identifiers": {"identifier_value", "identifier_type", "document_id", "query"},
```

**`PlanValidator._RETRIEVAL_TOOLS` — add:**
```python
"retrieve_identifiers"
```

**`PlanRepair._ALLOWED_ARGS` — add:**
```python
"retrieve_identifiers": {"identifier_value", "identifier_type", "document_id", "query"},
```

**`PlanPromptBuilder._TOOL_HINTS` — add:**
```python
"retrieve_identifiers": "Search for specific identifiers (part numbers, serial numbers, model numbers, order codes). Args: identifier_value (str), identifier_type (optional: 'part_number'|'serial_number'|'model_number'|'order_code'), document_id (optional).",
```

**`DeterministicPlanner.create_plan()` — add identifier compound plan:**
```python
# Trigger: query contains identifier pattern AND no existing compare/explore marker
if _contains_identifier_pattern(normalized_input):
    return _build_identifier_lookup_plan(state, normalized_input)
```

---

## 9. Files Affected

| File | Change Type | What Changes |
|------|-------------|-------------|
| `src/application/langgraph/planning/plan_policy.py` | Edit | Add `"retrieve_identifiers"` to `_DEFAULT_ALLOWED_TOOLS` |
| `src/application/langgraph/planning/plan_validator.py` | Edit | Add `retrieve_identifiers` to `_KNOWN_ARGS` and `_RETRIEVAL_TOOLS` |
| `src/application/langgraph/planning/plan_repair.py` | Edit | Add `retrieve_identifiers` to `_ALLOWED_ARGS` |
| `src/application/langgraph/planning/plan_prompt_builder.py` | Edit | Add `retrieve_identifiers` to `_TOOL_HINTS` with description |
| `src/application/langgraph/planning/deterministic_planner.py` | Edit | Add identifier compound plan type; add `_contains_identifier_pattern()` helper |
| `src/application/langgraph/research/planners/deterministic_research_planner.py` | Edit | Add `ResolveIdentifierTask` concept; add pre-fetch hint field |
| `tests/unit/planning/test_plan_policy.py` | Create | Tests for `retrieve_identifiers` in allowed tools |
| `tests/unit/planning/test_plan_validator.py` | Create/Edit | Tests for `retrieve_identifiers` arg validation and retrieval tool classification |
| `tests/unit/planning/test_plan_repair.py` | Create/Edit | Tests for `retrieve_identifiers` arg preservation through repair |
| `tests/unit/planning/test_plan_prompt_builder.py` | Create/Edit | Tests for `retrieve_identifiers` hint in built prompt |
| `tests/unit/planning/test_deterministic_planner.py` | Create/Edit | Tests for identifier compound plan creation |
| `tests/integration/planning/test_identifier_planning_e2e.py` | Create | End-to-end: identifier query → deterministic plan → executor dispatch |

---

## 10. Implementation Plan

### Phase 1: Unlock `retrieve_identifiers` in the policy layer (3 files)

**Priority:** Critical — without this, no LLM plan can ever include identifier retrieval.

1. **`plan_policy.py`** — add `"retrieve_identifiers"` to `_DEFAULT_ALLOWED_TOOLS`
2. **`plan_validator.py`** — add `retrieve_identifiers` to `_KNOWN_ARGS` and `_RETRIEVAL_TOOLS`
3. **`plan_repair.py`** — add `retrieve_identifiers` to `_ALLOWED_ARGS`

**Tests after Phase 1 (3 tests):**
- `test_plan_policy_allows_retrieve_identifiers` — `PlanPolicy()` has `retrieve_identifiers` in allowed tools
- `test_plan_validator_accepts_valid_retrieve_identifiers_step` — step with known args passes validation
- `test_plan_repair_preserves_retrieve_identifiers_args` — repair does not strip valid args

### Phase 2: Teach the LLM about `retrieve_identifiers` (1 file)

**Priority:** High — the LLM will not propose identifier retrieval without a tool hint.

4. **`plan_prompt_builder.py`** — add `retrieve_identifiers` entry to `_TOOL_HINTS` with a clear description of when to use it and its args

**Tests after Phase 2 (2 tests):**
- `test_plan_prompt_builder_includes_retrieve_identifiers_hint` — built prompt string contains `"retrieve_identifiers"`
- `test_plan_prompt_builder_hint_describes_identifier_types` — prompt hint mentions `part_number`, `serial_number`, `model_number`

### Phase 3: Add identifier compound plan types to `DeterministicPlanner` (1 file)

**Priority:** High — identifier queries must get a deterministic plan, not fall through to bare `answer_question`.

5. **`deterministic_planner.py`** — add:
   - `_IDENTIFIER_PATTERN = re.compile(r"\b([A-Z]{1,5}\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+|DN\s*\d+)\b")`
   - `_IDENTIFIER_TERMS` check (part number, serial number, model number, order code, etc.)
   - `_build_identifier_lookup_plan()` — creates `[retrieve_identifiers → answer_question]` steps
   - `_build_identifier_context_plan()` — creates `[retrieve_identifiers → retrieve_chunks → answer_question]` for context queries
   - `_build_identifier_maintenance_plan()` — creates `[retrieve_identifiers → retrieve_chunks(maintenance) → answer_question]`
   - `_build_identifier_specification_plan()` — creates `[retrieve_identifiers → retrieve_chunks(specification) → answer_question]`
   - `_build_identifier_compare_plan()` — creates `[retrieve_identifiers → retrieve_chunks → answer_question]` for compare queries
   - Trigger logic: check identifier pattern before other compound markers

**Tests after Phase 3 (8 tests):**
- `test_deterministic_planner_creates_identifier_lookup_plan` — "find part number HP-001" → identifier plan
- `test_deterministic_planner_identifier_plan_has_retrieve_identifiers_step` — first step is `retrieve_identifiers`
- `test_deterministic_planner_identifier_plan_has_answer_step` — final step is `answer_question` depending on retrieve
- `test_deterministic_planner_identifier_context_plan_has_retrieve_chunks` — "context for HP-001" → 3-step plan
- `test_deterministic_planner_identifier_maintenance_plan_filters_chunk_type` — "maintenance for HP-001" → chunk_types includes maintenance_procedure
- `test_deterministic_planner_identifier_specification_plan_filters_chunk_type` — "specification for FLT-100" → chunk_types includes technical_specification
- `test_deterministic_planner_identifier_compare_plan_created` — "compare HP-001 and HP-002" → compare plan
- `test_deterministic_planner_non_identifier_query_not_matched` — "what is maintenance interval" → no identifier plan

### Phase 4: Research planner identifier awareness (1 file)

**Priority:** Medium — research planner currently assigns `IDENTIFIER_LOOKUP` strategy hint but does no pre-fetch.

6. **`deterministic_research_planner.py`** — extract the matched identifier value from `_CATEGORY_PATTERNS` regex and pass it as a hint in `ResearchTask`; mark tasks as needing pre-fetch

**Tests after Phase 4 (3 tests):**
- `test_research_planner_extracts_identifier_value_from_query` — identifier pattern extracted into task hint
- `test_research_planner_identifier_task_has_strategy_hint` — task strategy hint is `IDENTIFIER_LOOKUP`
- `test_research_planner_non_identifier_query_has_no_identifier_hint` — plain semantic query has no identifier hint

### Phase 5: Integration verification (2 tests)

7. **`tests/integration/planning/test_identifier_planning_e2e.py`** — create:
   - `test_identifier_query_produces_valid_deterministic_plan` — full path from query string to `ExecutionPlan` with correct steps
   - `test_plan_validator_accepts_deterministic_identifier_plan` — the produced plan passes `PlanValidator`

### Phase 6: Manual verification

Run:
```bash
python scripts/demo_agent_cli.py
```

Verification queries:
1. `"find part number HP-001"` — should produce identifier lookup plan
2. `"what is the context for serial number SN-2024-001"` — should produce 3-step plan
3. `"what maintenance tasks reference HP-001"` — should produce maintenance plan
4. `"compare model HP-500 across documents"` — should produce compare plan

Expected observable behavior: plan steps logged show `retrieve_identifiers` as first step, not `answer_question`.

---

## Audit Questions — Direct Answers

| # | Question | Answer |
|---|----------|--------|
| 1 | Is the planner hybrid? | Yes, confirmed across all three planning subsystems |
| 2 | What classes constitute the planning system? | `CreatePlanNode`, `DeterministicPlanner`, `LLMPlanProposer`, `PlanParser`, `PlanValidator`, `PlanRepair`, `PlanExecutor` (task layer); `RetrievalStrategyService`, `DeterministicStrategySelector`, `StrategyAdvisor`, `RetrievalPlanBuilder` (retrieval layer); `DeterministicResearchPlanner`, `LLMResearchPlanner` (research layer) |
| 3 | How does LLM planning interact with deterministic? | LLM runs only if deterministic confidence < 0.8 or no deterministic plan; LLM plan must pass `PlanValidator`; if repair + re-validate fails, deterministic plan is used as fallback |
| 4 | What is the validator's whitelist mechanism? | `PlanPolicy.allowed_tools` set; `PlanValidator._KNOWN_ARGS` dict; both must be updated to add a new tool |
| 5 | How does plan repair work? | Renames known tool aliases, removes blocked tools, strips unknown args; runs before re-validation; is not a whitelist bypass |
| 6 | Is `retrieve_identifiers` reachable by LLM plans? | **No** — absent from `PlanPolicy._DEFAULT_ALLOWED_TOOLS`, `PlanValidator._KNOWN_ARGS`, `PlanRepair._ALLOWED_ARGS`, and `PlanPromptBuilder._TOOL_HINTS` |
| 7 | What deterministic compound plan types exist? | `list_and_find`, `compare`, `explore_and_answer`, `retrieve_and_answer` — no identifier type |
| 8 | How does the strategy advisor work? | Optional; triggered by `StrategyAdvisor.trigger_reason()` (low confidence, compare markers, multi-intent); calls LLM; validates response; merges with deterministic |
| 9 | What signals trigger IDENTIFIER_LOOKUP? | `_IDENTIFIER_PATTERN` regex match = 4.0 pts; identifier terms (`part no`, `serial number`, etc.) = 3.5 pts each; threshold for strong signal = 4.0 |
| 10 | What is the research planner doing with identifiers? | `_CATEGORY_PATTERNS` matches identifier pattern; assigns `strategy_hint=IDENTIFIER_LOOKUP` to `ResearchTask`; does NOT pre-fetch identifier value before semantic search |
| 11 | Where are tool names registered? | Tool registry (tool DI container); `PlanPolicy.allowed_tools`; `PlanValidator._KNOWN_ARGS`; `PlanPromptBuilder._TOOL_HINTS`; `PlanExecutor._build_request()` dispatch |
| 12 | What is the executor's dispatch mechanism? | `PlanExecutor._build_request(step)` matches `step.tool_name` to build the correct request object; `retrieve_identifiers` IS handled here — only the policy layer is broken |
| 13 | Are there any LLM plan bypass paths? | No — `CreatePlanNode` always passes LLM output through `PlanParser` → `PlanValidator`; repair path re-validates; fallback is deterministic plan, not unvalidated LLM output |
| 14 | What is the confidence threshold? | `deterministic_confidence_threshold = 0.8` in `CreatePlanNode`; below this, LLM path is attempted |
| 15 | What data model changes are needed? | No new domain models required; `PlanStep.args` (already a flexible dict) can carry `identifier_value`, `identifier_type`; `ResearchTask` may need `identifier_value: str \| None` field if pre-fetch is implemented |
