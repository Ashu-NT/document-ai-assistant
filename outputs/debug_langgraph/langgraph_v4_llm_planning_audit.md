# LangGraph V4 LLM Planning Audit

## Current V3 Planning Flow
- `IntentRouter` detects compound requests and routes them to `RouteType.PLANNED_TASK`.
- `CreatePlanNode` calls `DeterministicPlanner` only.
- `DeterministicPlanner` builds fixed `ExecutionPlan` instances for:
  - compare
  - explore + answer
  - retrieve + answer
  - list + find
- `ExecutePlanNode` forwards the validated-in-practice V3 plan to `PlanExecutor`.
- `PlanExecutor` executes only through `ToolRegistry` and supports one internal synthetic step:
  - `format_combined_answer`
- `PlanSummaryNode` formats the final response and respects `show_plan`.
- `DocumentAgentGraph` keeps V1/V2 behavior intact and sends `planned_task` through:
  - `route_request -> create_plan -> execute_plan -> plan_summary -> final_response`
- `scripts/agent_cli.py` already supports:
  - `--show-plan`
  - JSON output for validated plan data
  - trace output

## Missing V4 Pieces
- No LLM plan proposer exists.
- No planning prompt builder exists.
- No JSON plan parser exists.
- No formal plan validation policy exists.
- No plan repair stage exists.
- No deterministic confidence wrapper exists beyond ad hoc planner success/failure.
- `PlanStep` does not yet carry `source`.
- `ExecutionPlan` does not yet carry `source`.
- `AgentState` does not yet carry:
  - `llm_planning_enabled`
  - `planning_source`
  - `planning_errors`
  - `planning_warnings`
  - `raw_llm_plan`
  - `validated_plan`
- `CreatePlanNode` does not yet:
  - attempt LLM fallback
  - parse/validate/repair/revalidate
  - persist LLM planning diagnostics
- `GraphFactory` and `NodeFactory` do not yet inject:
  - `LLMPlanProposer`
  - `PlanPromptBuilder`
  - `PlanParser`
  - `PlanValidator`
  - `PlanPolicy`
  - `PlanRepair`
- `scripts/agent_cli.py` does not yet support:
  - `--llm-planning`
  - `--no-llm-planning`
  - `--show-raw-plan`
- Tracing does not yet capture the full V4 planning lifecycle:
  - deterministic-vs-LLM choice
  - parse result
  - validation result
  - repair changes
  - blocked tools
  - raw LLM plan gating

## Existing Tool Registry
| Tool name | Category | Mutates state? | Allow in LLM plan? | Notes |
|---|---|---:|---:|---|
| `list_documents` | documents | No | Yes | Read-only corpus discovery. |
| `find_document` | documents | No | Yes | Resolves document selection; may trigger clarification flow. |
| `document_details` | documents | No | Yes | Read-only metadata lookup. |
| `explore_document` | question_answering/doc exploration | No | Yes | Read-only structured exploration of a selected document. |
| `retrieve_chunks` | retrieval | No | Yes | Read-only evidence retrieval. |
| `answer_question` | question_answering | No business mutation | Yes | Uses QA workflow and may invoke answer generation, but still read-only from a document-state perspective. |
| `run_quality_gate` | evaluation | No document mutation | Yes, with caution | Evaluation/reporting oriented; may write a local report artifact. |
| `retrieval_trace` | evaluation | No document mutation | Yes, with caution | Retrieval debugging tool; may write trace output. |

## Security/Safety Risks
- Tool hallucination:
  - LLM may invent tool names not present in `ToolRegistry`.
- Invalid args:
  - wrong field names
  - missing required fields
  - oversized text blobs
  - malformed document selectors
- Unsafe mutation:
  - future ingestion/delete/reingestion tools must stay blocked by policy by default.
- Document leakage:
  - corpus-wide QA/retrieval when a selected document exists but the request is intended to remain scoped.
- Excessive step count:
  - plans that bloat into low-value chains or hidden loops.
- Prompt injection:
  - model may echo shell-like or infrastructure-like tool names.
- Plan JSON parse failure:
  - prose, markdown fences, partial JSON, trailing explanation.
- Dependency abuse:
  - step references to future or missing outputs.
- Ambiguous document escalation:
  - LLM may try to answer without first resolving document ambiguity.
- Unsafe evaluation side effects:
  - `retrieval_trace` and `run_quality_gate` are logically safe but may write local artifacts, so they should be allowed intentionally, not implicitly.

## Implementation Plan
1. Extend planning models conservatively.
   - Add `source` to `PlanStep` and `ExecutionPlan`.
   - Preserve V3 serialization compatibility.

2. Add safety-first planning primitives.
   - `PlanPolicy`
   - `PlanParser`
   - `PlanValidator`
   - `PlanRepair`
   - Keep them deterministic and independent of graph execution.

3. Add LLM proposal surface without execution authority.
   - `PlanPromptBuilder`
   - `LLMPlanProposer`
   - Use `LLMService` only for raw text proposal.
   - No tool calls, no workflow calls, no direct execution.

4. Upgrade `CreatePlanNode`.
   - Deterministic planner first.
   - Only if deterministic planning is absent or low-confidence:
     - propose
     - parse
     - validate
     - repair once
     - revalidate
   - Store planning diagnostics in state.
   - Reject invalid plans safely.

5. Extend graph state, graph result, CLI, and tracing.
   - Add LLM planning flags/state fields.
   - Add `--llm-planning`, `--no-llm-planning`, `--show-raw-plan`.
   - Keep raw plan hidden unless trace/debug allows it.

6. Add focused unit coverage before widening scope.
   - Start with policy/parser/validator/repair tests.
   - Then `CreatePlanNode` and graph integration.
   - Keep V3 deterministic tests intact as regression guards.
