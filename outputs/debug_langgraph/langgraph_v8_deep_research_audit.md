# LangGraph V8 Deep Research Audit

## Current Agent Capabilities
- V1: deterministic document agent routing, document lookup, retrieval, and QA through LangGraph nodes.
- V2: session memory, selected-document continuity, clarification flow, and interactive CLI support.
- V3: deterministic compound-request planning through `DeterministicPlanner`, `CreatePlanNode`, and `PlanExecutor`.
- V4: optional validated LLM planning through `LLMPlanProposer`, `PlanParser`, `PlanValidator`, and `PlanRepair`.
- V5: agent evaluation, thresholds, quality gate reporting, and CLI-driven eval execution.
- V6: reflection, retry retrieval, evidence merge, clarification recovery, and retry query generation.
- V7: retrieval-strategy selection, strategy planning, multi-tool retrieval execution, and strategy trace reporting.

## Current QA Path
- CLI/runtime entrypoint:
  - `scripts/agent_cli.py`
  - `build_agent_runtime()` wires DB session, vector store, retrieval workflow, QA workflow, tools, node factory, and graph factory.
- Graph entry:
  - `src/application/langgraph/graphs/document_agent_graph.py`
  - `DocumentAgentGraph.run()` builds `AgentState`, validates it, restores session memory, and enters `route_request`.
- Routing:
  - `src/application/langgraph/routing/intent_router.py`
  - Simple questions fall through to `RouteType.ANSWER_QUESTION`.
- QA node:
  - `src/application/langgraph/nodes/question_answering/answer_question_node.py`
  - Resolves selected document.
  - Optionally runs V7 retrieval-strategy selection and retrieval-plan execution.
  - Passes selected chunks into `AnswerQuestionTool` through `context_override_chunks`.
- QA workflow:
  - `src/application/workflows/question_answering/question_answering_workflow.py`
  - Uses `QuestionAnsweringRouter` to analyze the query.
  - Executes `RetrievalWorkflow`.
  - Applies query/context/post-answer guardrails.
  - Delegates final grounded answer generation to `AnswerGenerationService` when enabled.
- Answer generation:
  - `src/application/services/answer_generation/answer_generation_service.py`
  - Already has answer-intent analysis, structured-context organization, prompt building, and citation-aware answer output.

## Current Planning Path
- Planner package:
  - `src/application/langgraph/planning/`
- Deterministic path:
  - `DeterministicPlanner` recognizes compound requests such as compare/explore/retrieve-plus-answer.
  - Produces `ExecutionPlan` and `PlanStep` objects.
- Optional LLM path:
  - `CreatePlanNode` calls `LLMPlanProposer` only when enabled.
  - Output is parsed, validated, and optionally repaired before acceptance.
- Execution:
  - `PlanExecutor` executes plan steps only through `ToolRegistry`.
  - Existing safety pattern already forbids “LLM executes tools directly”.
- Strength for V8:
  - This is the exact architectural pattern V8 research planning should mirror.

## Current Retrieval Strategy Path
- Strategy package:
  - `src/application/langgraph/retrieval_strategy/`
- Main service:
  - `RetrievalStrategyService.select_and_plan()`
  - Reuses `RetrievalQueryAnalyzer`.
  - Extracts signals.
  - Chooses deterministic strategy first.
  - Optionally allows validated LLM strategy selection.
  - Produces validated retrieval plan and trace.
- Execution:
  - `RetrievalPlanExecutor`
  - Executes retrieval through application tools in `ToolRegistry`.
  - No direct Qdrant or repository calls from LangGraph.
- Current strengths relevant to V8:
  - strategy selection already exists as a reusable pre-retrieval reasoning layer
  - retrieval execution is already bounded and tool-mediated
  - strategy trace structure already fits research trace expansion

## Current Reflection Path
- Reflection package:
  - `src/application/langgraph/reflection/`
- Nodes:
  - `answer_question` -> `reflect_answer` -> `retry_retrieval`
- Main services and helpers:
  - `ReflectionService`
  - `EvidenceMerger`
  - `RetryQueryBuilder`
  - `ClarificationBuilder`
  - `RetrievalRetryPolicy`
- Current strengths relevant to V8:
  - bounded retry logic already exists
  - evidence merge pattern already exists
  - trace and diagnostics style is already established
- Current limitation for V8:
  - reflection is answer-review centric, not research-gap centric

## Missing Research Capabilities
- research task decomposition
- multi-hop retrieval
- cross-section evidence synthesis
- gap detection
- bounded follow-up research
- structured report generation

Additional concrete gaps in the current codebase:
- No `DEEP_RESEARCH` route exists in `RouteType`.
- `IntentRouter` has no research-style request detection.
- `AgentState` has no research-goal, research-plan, research-task, research-gap, or research-report fields.
- No research planner package exists parallel to planning/retrieval_strategy/reflection.
- No research executor exists to run multiple bounded retrieval tasks in dependency order.
- No research synthesis layer exists for comparison/report/checklist outputs.
- No research metrics exist in agent evaluation.
- CLI has no `--deep-research`, `--llm-research-planning`, `--show-research-plan`, or `--show-research-trace`.

## Existing Reusable Components
| Component | File | Reuse in V8 |
|---|---|---|
| Route/graph entry | `src/application/langgraph/graphs/document_agent_graph.py` | Add `DEEP_RESEARCH` branch while preserving V1-V7 flows |
| Intent routing | `src/application/langgraph/routing/intent_router.py` | Extend for research-style query detection |
| Serializable graph state | `src/application/langgraph/state/agent_state.py` | Add research state fields without changing result contract shape |
| Deterministic planner pattern | `src/application/langgraph/planning/deterministic_planner.py` | Mirror for deterministic research-task decomposition |
| Optional LLM proposal pattern | `src/application/langgraph/nodes/planning/create_plan_node.py` | Mirror for validated optional LLM research planning |
| Tool-only execution contract | `src/application/langgraph/factories/tool_registry.py` | Reuse as the only execution seam for research tasks |
| Retrieval strategy reasoning | `src/application/langgraph/retrieval_strategy/services/retrieval_strategy_service.py` | Reuse per research task to choose best retrieval strategy |
| Retrieval execution | `src/application/langgraph/retrieval_strategy/executors/retrieval_plan_executor.py` | Reuse for multi-hop evidence collection without duplicating retrieval logic |
| Retrieval engine | `src/application/workflows/retrieval/retrieval_workflow.py` | Keep unchanged; consume only through tools/V7 strategy layer |
| QA workflow override seam | `src/application/workflows/question_answering/question_answering_workflow.py` | Reuse answer-from-supplied-chunks behavior where task mini-answers are useful |
| Answer intent and structured context | `src/application/services/answer_generation/answer_generation_service.py` | Reuse synthesis/report prompting style and citation preservation patterns |
| Reflection evidence merger | `src/application/langgraph/reflection/services/evidence_merger.py` | Reuse merge/dedup design ideas for research evidence merger |
| Graph tracing | `src/application/langgraph/tracing/graph_run_recorder.py` | Reuse node timing/diagnostics trace conventions |
| Evaluation framework | `src/application/langgraph/evaluation/agent_eval_runner.py` | Extend with research-specific route and report metrics |
| CLI/runtime wiring | `scripts/agent_cli.py` | Add deep-research flags and runtime wiring without changing existing QA defaults |

## Affected Files
| Area | File | Change |
|---|---|---|
| New V8 package | `src/application/langgraph/research/` | Add grouped package for models, planners, executors, synthesizers, evaluators, prompts, policies, validation, services, tracing, constants |
| Routing enum | `src/application/langgraph/routing/route_type.py` | Add `DEEP_RESEARCH` |
| Router | `src/application/langgraph/routing/intent_router.py` | Detect research-style requests and preserve simple QA behavior |
| Graph state | `src/application/langgraph/state/agent_state.py` | Add serializable deep-research fields and flags |
| Request validation | `src/application/langgraph/validation/graph_request_validator.py` | Validate new deep-research booleans |
| Research nodes | `src/application/langgraph/nodes/research/` | Add plan/execute/evaluate/synthesize/summary nodes |
| Existing node exports | `src/application/langgraph/nodes/__init__.py` | Export new research nodes |
| Node factory | `src/application/langgraph/factories/node_factory.py` | Construct research services, planners, evaluators, and nodes |
| Graph factory | `src/application/langgraph/factories/graph_factory.py` | Pass research-capable nodes cleanly into graph construction |
| Main graph | `src/application/langgraph/graphs/document_agent_graph.py` | Add deep-research branch, post-research reflection path, and result serialization |
| Public exports | `src/application/langgraph/__init__.py` | Export V8 research types/services where appropriate |
| LangGraph settings | `src/config/settings/langgraph_setting.py` | Add deep-research enablement and LLM research planning flags |
| CLI | `scripts/agent_cli.py` | Add deep-research flags, runtime wiring, result formatting, and JSON support |
| Evaluation models | `src/application/langgraph/evaluation/agent_test_case.py` | Add research expectations/turn flags |
| Evaluation runner | `src/application/langgraph/evaluation/agent_eval_runner.py` | Score research routing, plan validity, task success, gap detection, report completeness, citation coverage |
| Eval thresholds | `src/application/langgraph/evaluation/agent_eval_thresholds.py` | Add V8 research metric thresholds |
| Eval config | `src/config/evaluation/agent_eval_cases.yaml` | Add research cases |
| Eval config | `src/config/evaluation/agent_eval_thresholds.yaml` | Add research thresholds |
| Eval script | `scripts/run_agent_eval.py` | Add research reporting and threshold output |

## Implementation Plan
1. Add the V8 research package skeleton with grouped subpackages and stable `__init__.py` exports.
2. Add `DEEP_RESEARCH` routing and research-style trigger detection, but keep deep research opt-in by flag or clear router match.
3. Add research models and policies first so the rest of the implementation has typed bounded contracts.
4. Implement deterministic research planning before any optional LLM planner.
5. Implement research-plan validation and safe repair mirroring the existing V4 planning pattern.
6. Implement research task execution strictly through `ToolRegistry`, reusing V7 retrieval strategy selection per task.
7. Implement evidence merge, context building, and bounded gap detection with at most one follow-up iteration.
8. Implement deterministic report synthesis first, then optional LLM synthesis behind policy.
9. Add research nodes and integrate the new route into `DocumentAgentGraph`, preserving fallback to normal QA when research is disabled or cannot proceed safely.
10. Extend CLI, agent state, and evaluation together so V8 remains traceable, testable, and backward compatible.

## Recommended Delivery Order
1. Audit complete.
2. Routing/state/settings/CLI flags.
3. Research models and policies.
4. Deterministic research planner plus validation.
5. Research executor and evidence services.
6. Gap detection and bounded follow-up.
7. Deterministic synthesis/report builder.
8. Nodes, graph integration, and final result serialization.
9. Evaluation and CLI verification.
10. Optional LLM research planner and optional LLM synthesis.
