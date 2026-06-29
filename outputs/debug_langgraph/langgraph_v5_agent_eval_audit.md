# LangGraph V5 Agent Evaluation Audit

## Current Agent Capabilities

### V1
- Deterministic single-turn CLI document agent via `scripts/agent_cli.py`
- Graph entrypoint through `src/application/langgraph/graphs/document_agent_graph.py`
- Route-based execution across document listing, document finding, exploration, retrieval, QA, and quality-gate actions

### V2
- Interactive CLI loop with `--interactive`
- Session continuity through `ConversationMemory` and `SessionStateStore`
- Selected-document memory persisted per session
- Current-document and clear-document session commands
- Clarification state carried across turns:
  - `pending_clarification`
  - `clarification_options`
  - `clarification_question`

### V3
- Deterministic multi-step planning through:
  - `DeterministicPlanner`
  - `PlanExecutor`
  - `PlanSummaryNode`
- Plan-aware graph routing for `planned_task`
- CLI display support with `--show-plan`

### V4
- Validated LLM fallback planning through:
  - `LLMPlanProposer`
  - `PlanParser`
  - `PlanValidator`
  - `PlanRepair`
  - `PlanPolicy`
- Safe tool-plan enforcement through `ToolRegistry` and validator/policy checks
- Raw and validated plan surfaces already available in `GraphResult.data`
- Graph trace already records:
  - `node_name`
  - `route`
  - `tool_name`
  - `plan_id`
  - `plan_goal`
  - `step_id`
  - `selected_document_id`
  - `success`
  - `error_code`
  - `diagnostics`

## Current Evaluation Coverage

### Retrieval Benchmark
- Application-level retrieval benchmark already exists under `src/application/evaluation/retrieval/`
- Existing capabilities include:
  - truth-set loading
  - seeded corpus manifest loading
  - benchmark case resolution
  - retrieval workflow evaluation
  - JSON/Markdown report writing
  - threshold-based quality gate

### Retrieval Quality Gate
- `src/application/evaluation/retrieval/retrieval_quality_gate.py`
- `src/application/evaluation/retrieval/retrieval_quality_thresholds.py`
- Existing thresholds are YAML-backed and loaded from:
  - `src/config/evaluation/retrieval_thresholds.yaml`

### LangGraph Unit Tests
- Current LangGraph coverage already validates:
  - route execution
  - memory-backed selected-document flow
  - clarification flow
  - plan creation and execution
  - validated LLM planning behavior
  - trace recorder structure

### CLI Tests
- `tests/unit/cli_scripts/test_agent_cli.py` already covers:
  - argument parsing
  - context display formatting
  - JSON result formatting
  - raw-plan output
  - interactive loop exit behavior

## Missing Agent-Level Evaluation

The repo has strong retrieval evaluation, but it does not yet evaluate the agent as a behavior system.

Missing deterministic evaluation coverage:
- route accuracy across realistic requests
- document selection correctness
- selected-document memory across multi-turn cases
- clarification correctness for ambiguous document selection
- CLI session isolation between cases
- required-tool / forbidden-tool compliance
- validated-plan tool policy checks at evaluation time
- unsafe request blocking as an explicit measurable metric
- document-scope safety for retrieved context
- answer content expectation checks
- LLM-planning safety as a benchmarked behavior

What already exists and can be reused:
- `DocumentAgentGraph.run(...)` is the correct runtime seam
- `GraphResult` already surfaces:
  - `route`
  - `success`
  - `diagnostics`
  - `trace`
  - `messages`
  - `data`
- `GraphResult.data` already includes:
  - selected document identifiers/titles
  - clarification data
  - answer
  - context chunks
  - citations
  - execution plan
  - validated plan
  - plan steps
  - plan results
  - planning warnings/errors

Current gap:
- No application package under `src/application/langgraph/evaluation/`
- No YAML/JSON-backed agent test-case loader
- No deterministic runner for multi-turn agent cases
- No agent-level summary metrics or gate
- No agent evaluation CLI

## Proposed Metrics

Primary deterministic metrics for V5:

| Metric | Source | Notes |
|---|---|---|
| `route_accuracy` | `GraphResult.route` | Final route of final turn |
| `document_selection_accuracy` | `GraphResult.data.selected_document_*` | Supports title substring or exact ID |
| `clarification_accuracy` | `GraphResult.diagnostics`, clarification fields | Based on clarification expectation |
| `unsafe_block_rate` | route/trace/tool checks | No forbidden tool execution on unsafe cases |
| `plan_validity_rate` | `validated_plan`, `plan_steps` | Required/forbidden plan tools checked deterministically |
| `document_scope_safety_rate` | `context_chunks[].document_id` | Ensures scoped retrieval stays on the intended document |
| `tool_policy_compliance_rate` | `trace.tool_name` + tool result keys + plan tools | Required tools appear, forbidden tools absent |
| `answer_expectation_rate` | `answer` / `response_text` | Required and forbidden phrases only; no LLM judge |

Per-case checks should remain deterministic and explainable.

## Proposed Test Case Format

Recommended structure:

```yaml
- case_id: AG-010
  name: Select document and ask follow-up
  description: Selected-document memory should carry into the second turn.
  tags: [memory, qa]
  metadata: {}
  inputs:
    - user_input: open FWC12
    - user_input: what are the maintenance intervals?
      allow_answer_generation: false
  expected:
    final_route: answer_question
    selected_document_contains: FWC12
    should_clarify: false
    required_tools: [find_document, answer_question]
    forbidden_tools: []
    required_plan_tools: []
    forbidden_plan_tools: []
    answer_must_contain: []
    answer_must_not_contain: []
    context_document_id: null
    unsafe_request_blocked: null
    success: true
```

Important design points:
- multi-turn supported from day one
- graph runtime only, no direct tool invocation
- stable broad expectations for seeded corpora
- no hard dependency on full UUIDs unless a case truly requires it

## Repo Reality Notes

### Config path convention
- The brief says `config/evaluation/...`
- The actual repo convention already in use is:
  - `src/config/evaluation/...`
- V5 should follow the existing repo convention for:
  - `src/config/evaluation/agent_eval_cases.yaml`
  - `src/config/evaluation/agent_eval_thresholds.yaml`

### Output path convention
- Retrieval benchmark writes under `storage_settings.evaluation_output_path / "retrieval"`
- V5 should follow the same convention under:
  - `storage_settings.evaluation_output_path / "agent"`

### Tool integration boundary
- Optional tool wrappers can be added under `src/application/tools/evaluation/`
- They should remain wrappers around the new runner/gate
- LangGraph evaluation should not call a tool that recursively invokes the graph again

## Affected Files

| Area | File | Change |
|---|---|---|
| Audit | `outputs/debug_langgraph/langgraph_v5_agent_eval_audit.md` | Add V5 audit report |
| LangGraph eval | `src/application/langgraph/evaluation/__init__.py` | New package export surface |
| LangGraph eval | `src/application/langgraph/evaluation/agent_test_case.py` | Add case/turn/expected dataclasses |
| LangGraph eval | `src/application/langgraph/evaluation/agent_eval_result.py` | Add turn/case/summary dataclasses |
| LangGraph eval | `src/application/langgraph/evaluation/agent_eval_loader.py` | Add YAML/JSON loader and validation |
| LangGraph eval | `src/application/langgraph/evaluation/agent_eval_runner.py` | Add multi-turn graph runner and checks |
| LangGraph eval | `src/application/langgraph/evaluation/agent_eval_report.py` | Add JSON/Markdown reporting |
| LangGraph eval | `src/application/langgraph/evaluation/agent_eval_thresholds.py` | Add threshold model + YAML loader |
| LangGraph eval | `src/application/langgraph/evaluation/agent_quality_gate.py` | Add threshold gate |
| Config | `src/config/evaluation/agent_eval_cases.yaml` | Add default agent evaluation cases |
| Config | `src/config/evaluation/agent_eval_thresholds.yaml` | Add default thresholds |
| CLI | `scripts/run_agent_eval.py` | Add agent-eval CLI |
| Optional tools | `src/application/tools/evaluation/*.py` | Only if a non-circular wrapper fits the current tool style |
| Tests | `tests/unit/application/langgraph/evaluation/*` | Add model/loader/runner/report/gate coverage |
| Tests | `tests/unit/cli_scripts/test_run_agent_eval.py` | Add CLI coverage |

## Implementation Plan

### Phase A
- Add the new `src/application/langgraph/evaluation/` package
- Implement case and result dataclasses first

### Phase B
- Implement YAML/JSON loader with deterministic validation
- Reuse `SchemaValidationError`
- Reuse `src/config/evaluation/` path convention

### Phase C
- Implement runner against `DocumentAgentGraph`-compatible runtime
- Support:
  - isolated session IDs per case
  - multi-turn continuity within a case
  - tag/case filtering
  - optional overrides for generation and LLM planning

### Phase D
- Implement deterministic checks and summary metric aggregation
- Keep all checks non-LLM and trace/data-driven

### Phase E
- Implement JSON/Markdown report writer and quality gate
- Mirror the retrieval benchmark writer/gate style

### Phase F
- Implement `scripts/run_agent_eval.py`
- Reuse the existing agent runtime build path rather than inventing a parallel stack

### Phase G
- Add a stable starter case set
- Focus first on deterministic, corpus-light cases:
  - routing
  - memory
  - clarification
  - planning safety
  - selected-document scope

### Phase H
- Add targeted unit tests for the new package and CLI
- Run:
  - `python -m pytest tests/unit/application/langgraph/evaluation -q`
  - `python -m pytest tests/unit/cli_scripts/test_run_agent_eval.py -q`
  - `python -m pytest tests/unit/application/langgraph -q`
  - `python -m pytest -q`

## Recommendation

Implement V5 directly on top of the existing graph result and trace contract.

Reason:
- the graph already exposes nearly all required evaluation signals
- current retrieval evaluation provides a strong structural template
- this keeps V5 additive and low-risk
- V1/V2/V3/V4 behavior can remain unchanged while becoming measurable
