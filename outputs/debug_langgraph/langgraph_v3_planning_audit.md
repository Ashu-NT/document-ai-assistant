# LangGraph V3 Planning Audit

## Current V2 Flow
- `DocumentAgentGraph.run()` builds `AgentState`, hydrates session state from `ConversationMemory`, validates the request/state, appends the user message, invokes the graph, then persists the assistant response.
- `RouteRequestNode` uses `IntentRouter` to deterministically classify the request into one existing route and resolves selected-document fallback for:
  - `answer_question`
  - `retrieve_evidence`
  - `retrieval_trace`
  - current-document exploration
- Current session/document continuity already works through:
  - `selected_document_id`
  - `selected_document_title`
  - `selected_document_file_name`
  - clarification memory
- One-step execution today is:
  - route request
  - optional `find_document`
  - one action node/tool
  - clarification or error handling if needed
  - final response
- Existing one-step action nodes call application tools only through `ToolRegistry`:
  - `list_documents`
  - `find_document`
  - `document_details`
  - `explore_document`
  - `retrieve_chunks`
  - `answer_question`
  - `run_quality_gate`
  - `retrieval_trace`
- CLI V2 behavior already supports:
  - one-shot mode
  - interactive mode
  - selected document memory via `--session-id`
  - answer generation toggle
  - `--show-context`
  - `--json`
  - `--trace`

## Missing V3 Flow
- No compound request detection in `IntentRouter`.
- No route for a planned multi-step task.
- No serializable planning models in `src/application/langgraph/`.
- No deterministic planner that converts compound requests into a small tool plan.
- No plan executor that runs multiple tool steps in order and stores intermediate results.
- No planning nodes in the graph.
- No plan-aware response summarization node.
- No plan-specific state fields in `AgentState`.
- No plan-aware tracing fields such as:
  - `plan_id`
  - step id
  - step tool name
  - plan fallback markers
- No CLI `--show-plan` visibility.
- No tests yet for:
  - compound-plan routing
  - plan creation
  - plan execution
  - plan summary formatting
  - V2 fallback when no plan is produced

## Affected Files
| Area | File | Change |
|---|---|---|
| Routing | `src/application/langgraph/routing/route_type.py` | Add `PLANNED_TASK` without changing existing route values. |
| Routing | `src/application/langgraph/routing/route_decision.py` | Add compound/planning metadata fields while preserving V2 decision structure. |
| Routing | `src/application/langgraph/routing/intent_router.py` | Detect deterministic compound requests and emit `PLANNED_TASK`; keep simple V2 commands unchanged. |
| State | `src/application/langgraph/state/agent_state.py` | Add serializable planning state fields and builder defaults. |
| Planning | `src/application/langgraph/planning/` | New package for `PlanStep`, `ExecutionPlan`, `DeterministicPlanner`, and `PlanExecutor`. |
| Nodes | `src/application/langgraph/nodes/planning/create_plan_node.py` | Create plan from current `AgentState`. |
| Nodes | `src/application/langgraph/nodes/planning/execute_plan_node.py` | Execute deterministic plans through `ToolRegistry` only. |
| Nodes | `src/application/langgraph/nodes/control/plan_summary_node.py` | Build readable multi-step response, optionally including the plan. |
| Nodes | `src/application/langgraph/nodes/__init__.py` | Export planning nodes. |
| Graph | `src/application/langgraph/graphs/document_agent_graph.py` | Add planned-task path, fallback behavior, result shaping, and plan data exposure. |
| Factories | `src/application/langgraph/factories/graph_factory.py` | Wire planner/executor-aware graph creation. |
| Factories | `src/application/langgraph/factories/tool_registry.py` | Likely no new external tools, but executor support should rely on current registered names. |
| Tracing | `src/application/langgraph/tracing/langgraph_trace.py` | Extend trace payload structure for plan-aware diagnostics. |
| Tracing | `src/application/langgraph/tracing/graph_run_recorder.py` | Record plan/step metadata and fallback markers. |
| CLI | `scripts/agent_cli.py` | Add `--show-plan`, pass flag into graph state, print or include plan output. |
| Package exports | `src/application/langgraph/__init__.py` | Re-export planning types if they become part of the stable package surface. |
| Tests | `tests/unit/application/langgraph/routing/test_intent_router.py` | Add planned-task routing coverage and ensure simple commands still stay V2. |
| Tests | `tests/unit/application/langgraph/graphs/test_document_agent_graph.py` | Add graph-path tests for planning, fallback, clarification, and selected-document reuse. |
| Tests | `tests/unit/application/langgraph/nodes/` | Add planning node and executor-focused tests. |
| Tests | `tests/unit/application/langgraph/factories/test_tool_registry.py` | Add executor/tool-registry safety coverage if needed. |
| Tests | `tests/unit/application/langgraph/tracing/test_graph_run_recorder.py` | Add plan-trace metadata assertions. |
| Tests | `tests/unit/cli_scripts/test_agent_cli.py` | Add `--show-plan` parsing and output coverage. |

## Implementation Plan
1. Add the planning model layer first.
   - Create `PlanStep` and `ExecutionPlan`.
   - Keep them fully serializable and easy to test in isolation.
2. Extend routing/state next.
   - Add `PLANNED_TASK`.
   - Add `RouteDecision` planning fields.
   - Add `AgentState` planning fields and defaults.
3. Implement deterministic planning in isolation.
   - Add `DeterministicPlanner` with a narrow set of V3-supported patterns only.
   - Do not weaken existing V2 routing.
4. Implement execution next.
   - Add `PlanExecutor` that uses only `ToolRegistry`.
   - Support ordered execution, dependency checks, failure stopping, and step result storage.
5. Add planning nodes and response summarization.
   - `CreatePlanNode`
   - `ExecutePlanNode`
   - `PlanSummaryNode`
6. Integrate the planning path into `DocumentAgentGraph`.
   - `PLANNED_TASK -> create_plan -> execute_plan -> plan_summary -> final_response`
   - If no plan is produced, fall back safely to normal V2 answer flow.
   - If a plan needs a document and none is available, reuse clarification flow.
7. Update tracing and CLI.
   - Add `--show-plan`.
   - Surface plan info in stdout and JSON output without breaking existing trace/context behavior.
8. Add tests in the same order.
   - planning models
   - planner
   - executor
   - nodes
   - graph
   - CLI
9. Run targeted suites first, then full pytest.
   - `tests/unit/application/langgraph`
   - `tests/unit/cli_scripts`
   - full suite
