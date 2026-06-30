# Enterprise Guardrails Audit

## Existing Guardrail Components

### Contracts and shared guardrail models

| File | Current role |
|---|---|
| `src/application/contracts/guardrails/guardrail.py` | Minimal `Guardrail` protocol with `check(context) -> GuardrailResult`. |
| `src/application/contracts/guardrails/guardrail_context.py` | Current context model for retrieval/QA guardrails only. Holds `query_text`, `document_id`, chunk lists, answer text, and metadata. Not yet graph/runtime wide. |
| `src/application/contracts/guardrails/guardrail_result.py` | Current result model. Supports `allowed`, `decision`, `reason`, `confidence`, chunk approval/rejection, citations, and `safe_user_message`. Missing enterprise decision/severity/tool-block/trace structure. |
| `src/application/contracts/guardrails/guardrail_decision.py` | Current decisions: `ALLOW`, `ALLOW_WITH_CAUTION`, `NEEDS_CLARIFICATION`, `OUT_OF_SCOPE`, `NO_EVIDENCE`, `LOW_CONFIDENCE`, `INSUFFICIENT_EVIDENCE`, `CITATION_REQUIRED`, `UNSUPPORTED_CLAIMS`, `SAFETY_BLOCKED`. |
| `src/application/contracts/guardrails/guardrail_violation.py` | Current violation model with `violation_type`, `message`, optional `chunk_id`, optional `field`. |
| `src/application/contracts/guardrails/violation_type.py` | Current violation enum focused on retrieval/answer quality. No prompt-injection, secret leakage, unsafe tool abuse, or grounding-failure categories yet. |
| `src/application/contracts/guardrails/confidence_level.py` | Current confidence enum. No severity model. |

### Guardrail orchestration

| File | Current role |
|---|---|
| `src/application/guardrails/guardrail_runner.py` | Linear short-circuit runner. Stops on first blocking guardrail and returns `None` when all pass. No trace, no layer info, no aggregated diagnostics. |
| `src/application/guardrails/context/context_guardrail_chain.py` | Specialized chain for chunk filtering. Threads `approved_chunks` forward across context guardrails. |

### Retrieval guardrails

| File | Current role |
|---|---|
| `src/application/guardrails/retrieval/query_scope_guardrail.py` | Detects off-topic or vague retrieval queries using deterministic text markers. Returns `OUT_OF_SCOPE` or `NEEDS_CLARIFICATION`. This is the closest existing pre-query scope guardrail. |
| `src/application/guardrails/retrieval/retrieval_evidence_guardrail.py` | Blocks retrieval results with zero or too few chunks. |
| `src/application/guardrails/retrieval/document_relevance_guardrail.py` | Checks retrieved chunks against requested chunk types and safety intent. |
| `src/application/guardrails/retrieval/identifier_evidence_guardrail.py` | Identifier-focused evidence validation. |
| `src/application/guardrails/retrieval/retrieval_confidence_guardrail.py` | Retrieval confidence threshold enforcement. |
| `src/application/guardrails/retrieval/__init__.py` | Re-exports current retrieval guardrails. |

### Context guardrails

| File | Current role |
|---|---|
| `src/application/guardrails/context/scoped_document_consistency_guardrail.py` | Removes or blocks chunks outside the selected document scope. |
| `src/application/guardrails/context/context_filtering_guardrail.py` | Filters low-value or noisy chunks. |
| `src/application/guardrails/context/context_quality_guardrail.py` | Checks context quality. |
| `src/application/guardrails/context/context_budget_guardrail.py` | Limits context size. |

### Answer guardrails

| File | Current role |
|---|---|
| `src/application/guardrails/answering/citation_guardrail.py` | Foundation stub only. Always allows if answer exists. |
| `src/application/guardrails/answering/unsupported_claim_guardrail.py` | Foundation stub only. Always allows if answer exists. |
| `src/application/guardrails/answering/safety_answer_guardrail.py` | Foundation stub only. Always allows if answer exists. |
| `src/application/guardrails/answering/unsupported_suggestion_guardrail.py` | Answer-stage guardrail placeholder. |
| `src/application/guardrails/answering/answer_support_guardrail.py` | Answer support validation placeholder/foundation. |

### Policies

| File | Current role |
|---|---|
| `src/application/guardrails/policies/enterprise_guardrail_policy.py` | Only a few booleans and thresholds: out-of-scope blocking, citations, min confidence, max context tokens. |
| `src/application/guardrails/policies/retrieval_guardrail_policy.py` | Retrieval thresholds and evidence requirements. |
| `src/application/guardrails/policies/answer_guardrail_policy.py` | Answer-stage toggles and claim-support score threshold. |
| `src/application/guardrails/policies/safety_guardrail_policy.py` | Safety-answer thresholds. |

### LangGraph routing and control

| File | Current role |
|---|---|
| `src/application/langgraph/routing/unsafe_action_detector.py` | Deterministic destructive corpus mutation detector. Only handles delete/wipe/drop/reingest style corpus requests. |
| `src/application/langgraph/routing/intent_router.py` | Main graph router. Applies `UnsafeActionDetector` before normal fallback, but does not run domain-scope, prompt-injection, secret, or tool-abuse guardrails. Unknown non-command input falls back to `ANSWER_QUESTION`. |
| `src/application/langgraph/routing/route_type.py` | Current route types include `BLOCKED_ACTION` but not `OUT_OF_SCOPE`. |
| `src/application/langgraph/nodes/control/route_request_node.py` | Stores route decision and blocked-action diagnostics on graph state. No unified guardrail result object. |
| `src/application/langgraph/nodes/control/blocked_action_node.py` | Produces a fixed destructive-operation block message. No policy-specific message builder. |
| `src/application/langgraph/nodes/control/final_response_node.py` | Resolves final response text and persists session state. No post-response sanitization or citation/grounding enforcement. |
| `src/application/langgraph/graphs/document_agent_graph.py` | Graph entry branch handles `blocked_action`; `_build_result()` surfaces unsafe-block diagnostics. No enterprise guardrail trace or out-of-scope branch. |
| `src/application/langgraph/state/agent_state.py` | Holds `unsafe_request_blocked`, `blocked_reason`, `blocked_terms`, and clarification flags, but no generic guardrail state object. |

### Planning, research, and tool safety checks

| File | Current role |
|---|---|
| `src/application/langgraph/planning/plan_validator.py` | Good deterministic pre-tool/pre-plan safety seam. Validates tool allowlist, mutating tool markers, unsafe tool markers, arg size, and document scope. Still planner-only and not built around a generic guardrail service. |
| `src/application/langgraph/research/validation/research_task_validator.py` | Blocks mutation-like research tasks and enforces document scope. Research-specific only. |
| `src/application/langgraph/factories/tool_registry.py` | Registered tools are explicit, which helps pre-tool control, but there is no centralized tool-execution guardrail policy yet. |

### QA workflow integration

| File | Current role |
|---|---|
| `src/application/workflows/question_answering/question_answering_workflow.py` | Already supports `pre_query_guardrails`, `context_guardrails`, and `post_answer_guardrails`. This is the strongest existing guardrail integration point. |
| `src/application/workflows/retrieval/retrieval_workflow.py` | Supports retrieval-time guardrails and evidence checks. |

### Runtime and presentation

| File | Current role |
|---|---|
| `src/application/agent_runtime/demo_agent_runtime.py` | Wires retrieval/context/post-answer guardrails, but currently does not wire `QueryScopeGuardrail` into QA runtime pre-query guardrails. |
| `src/application/agent_runtime/react_loop/react_trace_builder.py` | Shows blocked destructive requests in safe ReAct output. No out-of-scope/prompt-injection/secret guardrail presentation path yet. |
| `src/application/agent_runtime/presenters/console_presenter.py` | Renders final answers and context, but does not run a response sanitizer. |

### Evaluation

| File | Current role |
|---|---|
| `src/config/evaluation/agent_eval_cases.yaml` | Already contains some blocked destructive cases. No comprehensive out-of-scope, prompt-injection, secret, or post-response grounding suite yet. |
| `src/application/langgraph/evaluation/agent_eval_runner.py` | Tracks unsafe blocked state and routing accuracy. No enterprise guardrail metrics such as false positives, redirect rate, prompt-injection block rate, or grounding-failure catch rate. |

## Current Guardrail Flow

### Current graph flow

`User input`
-> `DocumentAgentGraph.run()`
-> `RouteRequestNode`
-> `IntentRouter.route()`
-> `UnsafeActionDetector.detect()` for destructive corpus mutation only
-> route branch
-> tool/workflow execution
-> `FinalResponseNode`
-> `_build_result()`

### Current QA/retrieval flow

`QuestionAnsweringWorkflow.run()`
-> optional `pre_query_guardrails` via `GuardrailRunner`
-> router/analyzed retrieval query
-> `RetrievalWorkflow.run()`
-> retrieval/context guardrails
-> optional answer generation
-> optional post-answer guardrails

### Where guardrails currently run

- Pre-route:
  - `UnsafeActionDetector` inside `IntentRouter`
- Pre-plan:
  - `PlanValidator`
  - `ResearchTaskValidator`
- Pre-retrieval / pre-query:
  - `QueryScopeGuardrail` exists, but only where explicitly wired
- Post-retrieval / context:
  - retrieval/context guardrails in retrieval + QA workflow
- Post-answer:
  - placeholder answer guardrails in QA workflow
- Runtime presentation:
  - blocked destructive requests shown in `ReactTraceBuilder`

### Where guardrails do not currently run well enough

- Before routing for out-of-scope general requests
- Before routing for prompt injection, secret requests, and hidden-prompt requests
- Before tool execution across the whole graph/runtime
- Before final response sanitization
- As a unified traced decision model across layers

## Current Weaknesses

1. Out-of-domain requests still route through the normal graph first.
   - `IntentRouter` only blocks destructive corpus mutation.
   - General requests such as weather/jokes/trivia currently fall back to `ANSWER_QUESTION` at the router level.
   - `QueryScopeGuardrail` exists but is not used as a graph-wide pre-route guardrail.

2. Scope guardrails are not consistently wired in runtime.
   - `demo_agent_runtime.py` wires context and post-answer guardrails, but not `pre_query_guardrails=[QueryScopeGuardrail()]`.
   - This means the strongest existing out-of-scope detector is not guaranteed to run in the main demo runtime path.

3. No unified enterprise guardrail result model exists.
   - Current `GuardrailResult` is retrieval/QA oriented.
   - Missing: severity, blocked tools, suggested actions, diagnostics contract, user-facing standardized message, trace id.

4. No clear separation of guardrail classes by boundary.
   - Current package is split by retrieval/context/answering, not by pre-route, pre-tool, pre-generation, post-response, or runtime presentation layers.

5. Prompt injection and secret leakage protections are missing.
   - No detector/policy for:
     - system prompt requests
     - chain-of-thought requests
     - `.env` / API key requests
     - arbitrary shell / PowerShell / command execution requests
     - “ignore previous instructions” style injection

6. Tool-execution guardrails are partial and planner-specific.
   - `PlanValidator` does useful allowlist and safety checks.
   - Non-plan graph actions do not pass through a generic pre-tool guardrail service.
   - Tool registry does not itself enforce per-route authorization decisions.

7. Post-answer guardrails are still mostly foundation stubs.
   - `citation_guardrail.py`, `unsupported_claim_guardrail.py`, and `safety_answer_guardrail.py` currently allow almost everything.
   - No real citation enforcement, no internal-id redaction, no grounding-failure fallback, no secret sanitization.

8. Final response node does not sanitize.
   - `FinalResponseNode` just resolves text and persists memory.
   - It does not remove internal IDs, raw prompt leakage, internal file paths, or unsupported claims.

9. No enterprise trace for blocked/redirected decisions.
   - There is graph trace and destructive-block diagnostics.
   - There is no dedicated guardrail trace capturing layer, policy, severity, matched terms, route, timestamp, and blocked tool.

10. No `OUT_OF_SCOPE` route in LangGraph.
    - Current graph has `BLOCKED_ACTION` but not a first-class out-of-scope redirect route.
    - User-facing out-of-scope handling is therefore not standardized at graph level.

11. Evaluation coverage is too narrow for enterprise guardrails.
    - Existing agent eval already checks some unsafe destructive cases.
    - Missing systematic cases and metrics for:
      - out-of-scope redirect
      - prompt injection block
      - secret request block
      - arbitrary shell block
      - grounding-failure catch
      - guardrail false positives

## Required Enterprise Guardrail Architecture

### Design principles

- Keep the existing repo structure style: grouped subpackages, no flat dump files.
- Reuse the current contracts and guards where possible, but upgrade them into a unified guardrail system.
- Make guardrail decisions deterministic first.
- Make all blocked/redirected results traceable and user-friendly.
- Keep routing, planning, tool execution, retrieval, answer generation, and final response as separate guardrail boundaries.

### Proposed package target

Use `src/application/guardrails/` as the main package and group by responsibility:

- `models/`
- `policies/`
- `detectors/`
- `services/`
- `messages/`
- `tracing/`
- `validation/`

### Proposed model upgrades

- Replace or adapt current contract-level models into a unified result system:
  - `GuardrailDecision`
  - `GuardrailSeverity`
  - `GuardrailViolation`
  - `GuardrailResult`
  - `GuardrailContext`
- Keep serialization-friendly dataclasses.
- Preserve backward compatibility where existing QA/retrieval paths rely on current `safe_user_message`, `approved_chunk_ids`, or `rejected_chunk_ids`.

### Proposed execution layers

1. Pre-route guardrails
   - domain scope
   - destructive unsafe requests
   - prompt injection
   - secret/env request
   - arbitrary command/tool abuse

2. Pre-planning guardrails
   - unsupported goals
   - missing document scope when required
   - unauthorized/destructive plan steps

3. Pre-tool guardrails
   - tool allowlist by route/runtime mode
   - destructive tool block in demo mode
   - argument abuse detection
   - document-scope preservation

4. Pre-generation guardrails
   - no evidence / weak evidence
   - wrong-document evidence
   - missing page/section/source metadata
   - out-of-scope question caught late

5. Post-response guardrails
   - citation requirement
   - grounding requirement
   - internal-id stripping
   - hidden-prompt / chain-of-thought stripping
   - secret/env/path stripping

6. Runtime presentation guardrails
   - clean guardrail trace for demo UI
   - friendly redirect/block messages
   - keep internal diagnostics only for debug mode

### Routing integration target

- Add first-class `OUT_OF_SCOPE` route support.
- Run pre-route guardrails before normal intent fallback.
- Reuse `BLOCKED_ACTION` for destructive/unsafe requests.
- Route `REDIRECT`/`OUT_OF_SCOPE` to a dedicated safe response node or extend blocked-action handling into generalized guardrail control handling.

## Files Affected

| File | Current Problem | Proposed Fix |
|---|---|---|
| `src/application/contracts/guardrails/guardrail_decision.py` | Current decision set is retrieval/QA centric. | Expand/normalize to enterprise decision model and keep compatibility shims where needed. |
| `src/application/contracts/guardrails/guardrail_result.py` | Missing severity, blocked tools, suggested actions, diagnostics contract, trace id. | Replace with richer model or migrate to `src/application/guardrails/models/guardrail_result.py` and re-export safely. |
| `src/application/contracts/guardrails/guardrail_context.py` | Too narrow for graph/runtime/final-response boundaries. | Expand into serializable enterprise guardrail context. |
| `src/application/guardrails/` | Organized by retrieval/context/answering only. | Reorganize into grouped enterprise subpackages while preserving stable imports where needed. |
| `src/application/langgraph/routing/intent_router.py` | Only destructive unsafe block; out-of-scope falls through to QA. | Run pre-route guardrail service before route fallback. |
| `src/application/langgraph/routing/route_type.py` | No `OUT_OF_SCOPE` route. | Add `OUT_OF_SCOPE` and related handling. |
| `src/application/langgraph/nodes/control/route_request_node.py` | No unified guardrail payload in state. | Persist guardrail decision/result/trace metadata. |
| `src/application/langgraph/nodes/control/blocked_action_node.py` | Hardcoded destructive-only message. | Generalize to policy-driven guardrail message rendering or pair with dedicated out-of-scope handler. |
| `src/application/langgraph/nodes/control/final_response_node.py` | No post-response sanitization. | Run post-response guardrail service before final output. |
| `src/application/langgraph/graphs/document_agent_graph.py` | No guardrail branches beyond blocked destructive action. | Add pre-route/out-of-scope flow and propagate guardrail trace/result to graph output. |
| `src/application/langgraph/planning/plan_validator.py` | Useful safety checks are isolated from enterprise guardrail model. | Reuse inside pre-planning/pre-tool guardrail service. |
| `src/application/agent_runtime/demo_agent_runtime.py` | Existing scope guardrail not wired pre-query. | Wire enterprise guardrails and preserve current retrieval/context/post-answer layering. |
| `src/application/agent_runtime/react_loop/react_trace_builder.py` | Only destructive safety block presentation exists. | Add out-of-scope, prompt-injection, secret, and insufficient-evidence guardrail presentations. |
| `src/application/agent_runtime/presenters/console_presenter.py` | No response sanitization layer. | Consume sanitized graph output only; keep debug info behind policy. |
| `src/config/evaluation/agent_eval_cases.yaml` | Missing broad enterprise guardrail suite. | Add out-of-scope, injection, secret, shell-abuse, and evidence-failure cases. |
| `src/application/langgraph/evaluation/agent_eval_runner.py` | Missing enterprise guardrail metrics. | Add redirect/block/false-positive/false-negative/grounding-catch metrics. |

## Implementation Plan

### Phase 1: Model and package foundation

- Create grouped `src/application/guardrails/` structure.
- Introduce enterprise guardrail models:
  - decision
  - severity
  - violation
  - result
  - context
- Preserve `src.` import stability through `__init__.py` re-exports.

### Phase 2: Deterministic detectors and policies

- Add detectors for:
  - domain scope
  - unsafe destructive actions
  - prompt injection
  - secret leakage requests
  - tool abuse / arbitrary command requests
  - grounding/citation failure
- Keep benchmark/runtime safety deterministic first.

### Phase 3: Guardrail services

- Add:
  - `pre_route_guardrail_service.py`
  - `pre_tool_guardrail_service.py`
  - `pre_generation_guardrail_service.py`
  - `post_response_guardrail_service.py`
  - `guardrail_service.py`
- Make each boundary explicit and testable.

### Phase 4: LangGraph integration

- Run pre-route guardrails before normal routing fallback.
- Add `OUT_OF_SCOPE` handling.
- Persist guardrail result and trace info on graph state.
- Reuse final response node for user-safe messaging.

### Phase 5: Runtime integration

- Update demo runtime wiring to use pre-query scope guardrails.
- Show clean trace entries for redirect/block decisions.
- Keep debug detail hidden unless requested.

### Phase 6: Post-response safety

- Sanitize internal IDs, prompt leakage, secret-like text, and unsupported final answer content.
- Enforce safe fallback for missing grounding/citations when required.

### Phase 7: Evaluation and tests

- Expand agent evaluation cases and metrics.
- Add unit tests for each detector, policy, service, routing integration, graph integration, and runtime presentation.

## Audit Summary

The codebase already has a solid retrieval/QA guardrail foundation, plus useful planner safety checks and destructive corpus blocking. The main enterprise gap is not the absence of all guardrails; it is the absence of a unified, graph-wide, layer-aware guardrail system.

The biggest current risks are:

- out-of-scope requests falling into normal QA routing
- missing prompt-injection/secret/tool-abuse handling
- post-answer guardrails still being mostly stubs
- no final-response sanitization
- no first-class out-of-scope route or enterprise guardrail trace

This audit was created before code changes, as required.
