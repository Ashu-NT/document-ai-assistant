# LangGraph V6 Reflection Audit

## Current QA Path

### Route
- `DocumentAgentGraph.run()` builds `AgentState`, restores session memory, validates the request/state, appends the user message to memory, invokes the graph, then builds the final `GraphResult`.
- `route_request` decides between direct action routes, planned-task routing, blocked-action routing, and clarification routing.
- For question answering, the current path is:
  - `route_request`
  - optional `find_document`
  - `answer_question`
  - `final_response`
- For retrieval-only requests, the current path is:
  - `route_request`
  - optional `find_document`
  - `retrieve_evidence`
  - `final_response`
- Planned tasks currently go through:
  - `route_request`
  - `create_plan`
  - `execute_plan`
  - `plan_summary`
  - `final_response`

### Retrieval
- `AnswerQuestionNode` calls `AnswerQuestionTool`.
- `AnswerQuestionTool` converts the CLI/graph request into `QuestionAnsweringRequest` and delegates to `QuestionAnsweringWorkflow`.
- `QuestionAnsweringWorkflow` currently performs a single retrieval pass:
  1. optional pre-query guardrails
  2. `QuestionAnsweringRouter.decide(...)`
  3. `RetrievalWorkflow.run(...)`
  4. context guardrail chain on `workflow_result.final_chunks`
  5. explicit document-scope guardrail check
  6. answer generation from approved chunks only
  7. post-answer guardrails
- `RetrievalWorkflow` already has deterministic query enrichment:
  - identifier extraction
  - deterministic rewrite/normalization
  - intent inference
  - chunk-type preference mapping
- `RetrievalWorkflow` also already has:
  - pre/post retrieval guardrail hooks
  - candidate-pool expansion
  - deduplication
  - selected-document scope enforcement
  - context expansion

### Answer Generation
- `QuestionAnsweringWorkflow` creates `AnswerGenerationRequest` with approved chunks only.
- `AnswerGenerationService` already has:
  - answer intent analysis
  - structured context organization
  - prompt building
  - citation generation
- `QuestionAnsweringResult` already surfaces:
  - `answer_text`
  - `retrieval_result`
  - `approved_chunk_ids`
  - `rejected_chunk_ids`
  - `citations`
  - `answer_intent`
  - `diagnostics`

### Guardrails
- Guardrails are active at multiple layers already and must remain in the V6 path:
  - unsafe request blocking in the router
  - pre-query guardrails in `QuestionAnsweringWorkflow`
  - retrieval pre/post guardrails in `RetrievalWorkflow`
  - context guardrails in `QuestionAnsweringWorkflow`
  - explicit document-scope guardrail in `QuestionAnsweringWorkflow`
  - post-answer guardrails in `QuestionAnsweringWorkflow`

### CLI Output
- `scripts/agent_cli.py` already supports:
  - `--generate`
  - `--show-context`
  - `--llm-planning`
  - `--show-plan`
  - `--show-raw-plan`
  - `--json`
  - `--trace`
- The CLI already prints:
  - route
  - success
  - response text
  - answer intent
  - context chunks
  - trace
- JSON output already includes:
  - route
  - success
  - answer
  - answer_intent
  - document selection fields
  - pending clarification
  - context chunks
  - citations
  - planning fields
  - diagnostics

## Current Retry Behavior

### Whether retry exists
- There is no answer-review reflection loop in the current graph.
- There is no retrieval retry node in the current graph.
- There is no bounded retry state in `AgentState`.

### Whether query rewrite exists
- Yes, but only as deterministic query normalization inside `RetrievalQueryAnalyzer`.
- Current rewrite behavior is limited to:
  - punctuation normalization
  - common identifier synonym normalization
  - query text cleanup
- This is not a retry planner and does not inspect:
  - initial answer quality
  - missing evidence
  - approved/rejected chunk diagnostics

### Whether evidence merge exists
- No V6-style evidence merge currently exists.
- Retrieval deduplication exists inside `RetrievalWorkflow`, but only within one retrieval pass.
- `QuestionAnsweringWorkflow` currently sends only the approved chunks from that one pass into answer generation.
- There is no current public seam for:
  - initial chunks + retry chunks
  - merged evidence reranking/trimming
  - answer regeneration from explicit merged chunks

### Current architecture limitation for V6 retry
- `QuestionAnsweringRequest` does not support a context override.
- `AnswerQuestionTool` does not support a context override.
- `QuestionAnsweringWorkflow` always calls `RetrievalWorkflow` itself for retrieval QA.
- If true merged-evidence answer regeneration is required, the cleanest seam is likely:
  - optional `context_override_chunks` on `QuestionAnsweringRequest`
  - or a narrower workflow/service seam just above answer generation
- This seam does not exist yet.

## Current Clarification Behavior

### Document clarification
- Clarification already exists for:
  - numeric option replies
  - document disambiguation
  - document-selection continuity across turns
- `IntentRouter` maps numeric replies like `1` or `option 1` to `CLARIFICATION_RESPONSE`.
- `ClarifyRequestNode` currently resolves document-selection clarification only.
- When document clarification is resolved, the state is updated with:
  - `document_id`
  - `document_title`
  - `selected_document_id`
  - `selected_document_title`
  - `selected_document_file_name`

### Missing reflection clarification
- There is no existing reflection-specific clarification kind.
- `pending_clarification` exists, but current behavior assumes document-selection semantics.
- There is no current resume payload for:
  - original question
  - reflection clarification answer
  - resume route for re-entering answer generation

### Session resume behavior
- `ConversationMemory` persists:
  - history
  - selected document fields
  - pending clarification
  - clarification options
  - clarification question
- `SessionStateStore` persists those values to disk as JSON.
- `DocumentAgentGraph.run()` restores those values before execution.
- `FinalResponseNode` persists session state back through memory.
- This is a good foundation for resumable reflection clarification, but the stored payload shape must be extended.

## Reflection Insertion Points

### Primary graph insertion point
- The cleanest insertion point is after `answer_question` and before `final_response`.
- Recommended answer path for V6:
  - `answer_question`
  - `reflect_answer`
  - branch to:
    - `final_response`
    - `retry_retrieval`
    - `clarify_request`
    - `error_handler` or safe fail path

### Planned-task insertion point
- For V6 scope control, reflect only the final planned answer rather than each intermediate plan step.
- Current planned flow already converges into `plan_summary`, which is the safest seam for optional final reflection later if needed.
- Recommended initial implementation:
  - direct answer-question flow first
  - planned-task final reflection second, only if stable

### State insertion points
- `AgentState` needs serializable reflection fields for:
  - enablement
  - show/hide reflection diagnostics
  - reflection attempt count
  - retrieval retry count
  - reflection result snapshot
  - retry query
  - initial/retry/merged context chunk payloads
  - reflection trace

### Tool/workflow seam
- `AnswerQuestionTool` and `QuestionAnsweringWorkflow` are the narrowest reusable seams if merged-evidence answer regeneration is implemented properly.
- `RetrieveChunksTool` is the safest seam for retry evidence collection without duplicating retrieval logic.

### CLI insertion points
- `scripts/agent_cli.py` needs new flags and output blocks for:
  - `--reflection`
  - `--no-reflection`
  - `--show-reflection`
- JSON output also needs reflection diagnostics if V6 is enabled.

### Evaluation insertion points
- `AgentEvalRunner`, report/result models, thresholds, and CLI wrapper already exist and can absorb reflection metrics without creating a parallel evaluation system.

## Affected Files

| Area | File | Change |
|---|---|---|
| Graph routing | `src/application/langgraph/graphs/document_agent_graph.py` | Insert reflection/retry branching and return reflection diagnostics in `GraphResult` data. |
| Graph state | `src/application/langgraph/state/agent_state.py` | Add serializable reflection, retry, clarification-resume, and merged-evidence fields. |
| QA node | `src/application/langgraph/nodes/question_answering/answer_question_node.py` | Preserve answer/retrieval payloads for reflection input. |
| New QA node | `src/application/langgraph/nodes/question_answering/reflect_answer_node.py` | Run reviewer logic and write structured decision back to state. |
| New QA node | `src/application/langgraph/nodes/question_answering/retry_retrieval_node.py` | Execute bounded retry retrieval, merge evidence, and prepare regeneration. |
| Clarification | `src/application/langgraph/nodes/control/clarify_request_node.py` | Support reflection clarification kind and resumable payloads. |
| Session persistence | `src/application/langgraph/memory/conversation_memory.py` | Persist expanded clarification/reflection state. |
| Session persistence | `src/application/langgraph/memory/session_state_store.py` | Persist expanded serializable reflection state. |
| Factories | `src/application/langgraph/factories/node_factory.py` | Register reflection/retry nodes and services. |
| Factories | `src/application/langgraph/factories/graph_factory.py` | Wire reflection-enabled graph creation without breaking existing defaults. |
| New package | `src/application/langgraph/reflection/...` | Add reflection models, prompts, services, policies, validation, tracing, constants. |
| Tool seam | `src/application/tools/question_answering/answer_question_tool.py` | Potentially pass optional context override if merged-evidence regeneration is implemented cleanly. |
| Workflow seam | `src/application/workflows/question_answering/question_answering_request.py` | Potentially add optional override context / retry metadata in a backward-compatible way. |
| Workflow seam | `src/application/workflows/question_answering/question_answering_workflow.py` | Support regeneration from merged evidence if enabled by the new seam. |
| CLI | `scripts/agent_cli.py` | Add reflection flags and reflection output/JSON support. |
| Eval | `src/application/langgraph/evaluation/*` | Add reflection-related metrics and report fields. |
| Eval CLI | `scripts/run_agent_eval.py` | Surface reflection-enabled evaluation runs. |
| Eval config | `config/evaluation/agent_eval_cases.yaml` | Add V6-specific coverage cases. |
| Tests | `tests/unit/application/langgraph/reflection/...` | Add reflection package tests. |
| Tests | existing LangGraph / CLI / workflow tests | Update for new optional state and routing behavior. |

## Implementation Plan

### Phase A - Additive foundation only
- Create `src/application/langgraph/reflection/` with:
  - models
  - policies
  - prompt builder
  - JSON parser
  - validator
  - tracing constants
- Keep this phase graph-independent and fully unit-testable.

### Phase B - Deterministic-safe reflection service
- Add `ReflectionService` with:
  - deterministic quality checks
  - optional LLM reviewer call
  - fallback behavior when LLM is unavailable
- Keep the service side-effect free:
  - no retrieval
  - no graph routing
  - no tool execution

### Phase C - Evidence merge and retry planning
- Add:
  - `EvidenceMerger`
  - `RetryQueryBuilder`
  - `ClarificationBuilder`
- Preserve selected-document scope during retry.
- Bound both counters to one attempt each.

### Phase D - Graph integration
- Extend `AgentState`.
- Add:
  - `ReflectAnswerNode`
  - `RetryRetrievalNode`
- Update graph routing so direct QA becomes:
  - `answer_question`
  - optional `reflect_answer`
  - `retry_retrieval` or `clarify_request` or `final_response`

### Phase E - Regeneration seam
- Preferred implementation:
  - add a backward-compatible optional `context_override_chunks` seam to question answering
  - regenerate from merged evidence when retry succeeds
- Fallback implementation if the seam becomes too invasive:
  - collect retry evidence
  - preserve merged evidence in diagnostics
  - rerun QA on the retry query
  - explicitly document the limitation
- Recommendation:
  - attempt the clean seam first because it best satisfies the V6 requirement that initial evidence is preserved and reused.

### Phase F - Clarification recovery
- Extend pending clarification payload shape to support:
  - `kind = reflection_clarification`
  - original user input
  - resume route
  - resume payload
- Resume the original QA path after the user replies, while preserving selected document and session continuity.

### Phase G - CLI and evaluation
- Add reflection flags to the CLI with default disabled behavior.
- Add reflection diagnostics to JSON and formatted output.
- Extend evaluation/reporting with reflection metrics.
- Keep V1-V5 behavior identical when reflection is disabled.

## Recommended guardrails for implementation
- Reflection must be disabled by default for compatibility.
- Reflection must never produce the user-facing answer.
- Retry must preserve the current selected document scope.
- Retry must not bypass current retrieval, context, or answer guardrails.
- Retry and reflection counts must be explicit in state and validated centrally.
- Avoid storing prompts or large raw payloads in session state; keep session snapshots compact and serializable.

## Current Risk Notes
- The largest architectural risk is merged-evidence answer regeneration because the current QA workflow owns retrieval internally.
- The safest way to avoid a hack is to add one narrow override seam rather than duplicating retrieval/answer logic in graph nodes.
- Planned-task reflection should be deferred until direct QA reflection is stable to avoid multiplying branch complexity too early.
