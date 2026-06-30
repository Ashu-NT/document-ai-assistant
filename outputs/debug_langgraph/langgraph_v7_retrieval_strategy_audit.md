# LangGraph V7 Retrieval Strategy Audit

## Current Retrieval Flow

### From CLI
- `scripts/agent_cli.py`
- CLI builds runtime in `build_agent_runtime()`.
- Runtime wires `ToolRegistry` with:
  - `retrieve_chunks`
  - `answer_question`
  - document tools
  - evaluation tools
- CLI calls `DocumentAgentGraph.run(...)`.

### From LangGraph
- `DocumentAgentGraph.run()` builds `AgentState`, validates it, then enters `route_request`.
- For explicit retrieval routes:
  - `route_request` -> `retrieve_evidence`
- For QA routes:
  - `route_request` -> `answer_question`
- For reflection retry:
  - `answer_question` -> `reflect_answer` -> `retry_retrieval`

### From `RetrieveEvidenceNode`
- File: `src/application/langgraph/nodes/question_answering/retrieve_evidence_node.py`
- Current behavior:
  - resolves selected document via `resolve_selected_document()`
  - always requires `retrieve_chunks`
  - sends only:
    - `query_text`
    - `document_id`
    - `top_k`
- No strategy selection exists yet.
- No use of `retrieve_tables`, `retrieve_identifiers`, or `retrieve_figures`.

### From `AnswerQuestionNode`
- File: `src/application/langgraph/nodes/question_answering/answer_question_node.py`
- Current behavior:
  - always requires `answer_question`
  - passes:
    - `question`
    - `document_id`
    - `top_k`
    - generation/context flags
- The node does not select retrieval strategy itself.
- It serializes returned retrieval context chunks into graph state for V6 reflection.

### From `AnswerQuestionTool`
- File: `src/application/tools/question_answering/answer_question_tool.py`
- Tool builds `QuestionAnsweringRequest` and delegates to `QuestionAnsweringWorkflow`.
- Existing seam already supports:
  - `context_override_chunks`
  - `retry_query`
- This is the cleanest current seam for future V7 strategy-selected evidence reuse.

### From `QuestionAnsweringWorkflow`
- File: `src/application/workflows/question_answering/question_answering_workflow.py`
- Router first builds an analyzed `RetrievalQuery` through `QuestionAnsweringRouter`.
- If no override chunks are provided:
  - `_handle_retrieval()` calls `RetrievalWorkflow.run(analyzed_query)`.
- If override chunks are provided:
  - `_build_override_workflow_result()` bypasses retrieval execution and answers from supplied chunks.
- Answer intent is resolved after retrieval/context approval, not before retrieval.

### From `RetrieveChunksTool`
- File: `src/application/tools/retrieval/retrieve_chunks_tool.py`
- Tool converts request into `RetrievalQuery`.
- Supported request inputs already include:
  - `document_types`
  - `chunk_types`
  - `use_dense`
  - `use_keyword`
  - `use_sql`
  - `trace`
- Tool then calls `RetrievalWorkflow.run(query, trace_recorder=...)`.

### From `RetrievalWorkflow`
- File: `src/application/workflows/retrieval/retrieval_workflow.py`
- Current flow already does:
  - deterministic query analysis
  - validation
  - optional pre-guardrails
  - retrieval via `HybridRetrievalService`
  - deduplication
  - scope filtering
  - optional post-guardrails
  - context expansion
  - trace recording
- This is the retrieval engine and should not be rewritten for V7.

## Current Retrieval Inputs
- Raw user question from CLI / graph state
- `document_id`
- `top_k`
- `document_types` on `RetrieveChunksRequest` / `RetrievalQuery`
- `chunk_types` on `RetrieveChunksRequest` / `RetrievalQuery`
- Retrieval backend toggles:
  - `use_dense`
  - `use_keyword`
  - `use_sql`
- `trace`
- `retry_query` in V6 retry path
- `context_override_chunks` in QA tool/workflow

## Current Retrieval Weaknesses
- Generic graph retrieval path always uses `retrieve_chunks`.
- Specialized retrieval tools exist but are not wired into `ToolRegistry` or runtime:
  - `retrieve_tables`
  - `retrieve_identifiers`
  - `retrieve_figures`
- `RetrieveEvidenceNode` does not exploit existing chunk/document filters or retrieval mode toggles.
- `AnswerQuestionNode` delegates to a generic QA path without pre-answer strategy selection.
- Reflection retry only changes query text/top-k today, not retrieval strategy.
- No explicit trace object exists for:
  - strategy signals
  - strategy choice
  - fallback reason
  - multi-strategy plan

### Query classes the current system already understands well
- Identifier-heavy wording
- Procedure / maintenance wording
- Troubleshooting wording
- Figure / table wording
- Overview / exploration wording

### Where the generic path is currently too blunt
- Table-heavy questions
- Identifier lookups
- Drawing / figure lookups
- Certification lookups
- Multi-evidence questions such as maintenance + specification
- Retry behavior after reflection when missing evidence type is known

## Existing Strategy Signals

### Signals already available before retrieval
- Route from `IntentRouter`
- Selected document / explicit document scope
- Raw user wording
- `top_k`
- Existing retrieval question analysis from `QuestionAnsweringRouter`:
  - detected identifiers
  - rewritten query
  - inferred retrieval intent
  - preferred chunk types

### Signals already available after retrieval / answer generation
- Answer intent from `AnswerGenerationService`
- Reflection decision / retry query
- Approved vs rejected context chunks

### Important current limitation
- Pre-retrieval graph state does not currently carry answer intent.
- `document_type` is supported by retrieval requests but is not populated by LangGraph today.
- Therefore V7 deterministic strategy selection should primarily rely on:
  - user wording
  - analyzed retrieval query
  - selected document presence
  - route
  - retry/reflection hints

## Where Strategy Selection Should Be Inserted

### Primary insertion point
- `src/application/langgraph/nodes/question_answering/retrieve_evidence_node.py`
- Rationale:
  - this node already owns evidence retrieval for explicit retrieval requests
  - it currently calls only `retrieve_chunks`
  - it is the cleanest place to switch from “one generic tool call” to “strategy select -> plan -> execute”

### Secondary insertion point
- `src/application/langgraph/nodes/question_answering/answer_question_node.py`
- Rationale:
  - QA path should be able to choose retrieval strategy before answer generation
  - best existing seam is to retrieve strategy-selected evidence first, then pass it through `context_override_chunks` to `AnswerQuestionTool`
  - fallback must preserve current behavior if strategy execution is disabled or fails

### Reflection retry insertion point
- `src/application/langgraph/nodes/question_answering/retry_retrieval_node.py`
- Rationale:
  - V6 retry already rebuilds a query and re-retrieves
  - V7 should let retry policy request a different retrieval strategy, not only a different query

### Construction / wiring points
- `src/application/langgraph/factories/node_factory.py`
- `src/application/langgraph/factories/graph_factory.py`
- `scripts/agent_cli.py`
- `src/config/settings/langgraph_setting.py`

### Evaluation insertion points
- `src/application/langgraph/evaluation/agent_test_case.py`
- `src/application/langgraph/evaluation/agent_eval_runner.py`
- `src/application/langgraph/evaluation/agent_eval_thresholds.py`
- `src/config/evaluation/agent_eval_cases.yaml`
- `src/config/evaluation/agent_eval_thresholds.yaml`
- `scripts/run_agent_eval.py`

## Files Affected

| Area | File | Change |
|---|---|---|
| New V7 package | `src/application/langgraph/retrieval_strategy/` | Add grouped package for models, selectors, planners, executors, policies, validation, services, prompts, tracing, constants |
| Graph state | `src/application/langgraph/state/agent_state.py` | Add serializable retrieval-strategy state fields |
| Retrieval node | `src/application/langgraph/nodes/question_answering/retrieve_evidence_node.py` | Replace direct `retrieve_chunks` call with strategy select -> plan -> execute |
| QA node | `src/application/langgraph/nodes/question_answering/answer_question_node.py` | Optionally answer from strategy-selected evidence while preserving fallback |
| Retry node | `src/application/langgraph/nodes/question_answering/retry_retrieval_node.py` | Let retry policy request strategy-aware retry execution |
| Node construction | `src/application/langgraph/factories/node_factory.py` | Inject V7 services and executor |
| Graph/runtime construction | `src/application/langgraph/factories/graph_factory.py` | Pass strategy-enabled nodes cleanly |
| Tool registry | `src/application/langgraph/factories/tool_registry.py` | Register specialized retrieval tools and allow plan validation against them |
| CLI runtime | `scripts/agent_cli.py` | Wire specialized retrieval tools, new flags, new output formatting |
| LangGraph settings | `src/config/settings/langgraph_setting.py` | Add V7 enable/disable and optional LLM selector config |
| Public exports | `src/application/langgraph/__init__.py` | Export V7 types/services where appropriate |
| Evaluation models | `src/application/langgraph/evaluation/agent_test_case.py` | Add expected strategy fields if needed |
| Evaluation runner | `src/application/langgraph/evaluation/agent_eval_runner.py` | Score strategy selection/trace/fallback metrics |
| Evaluation thresholds | `src/application/langgraph/evaluation/agent_eval_thresholds.py` | Add V7 metric thresholds |
| Eval config | `src/config/evaluation/agent_eval_cases.yaml` | Add V7 cases |
| Eval config | `src/config/evaluation/agent_eval_thresholds.yaml` | Add V7 thresholds |
| Eval script | `scripts/run_agent_eval.py` | Print/report V7 metrics |

## Implementation Plan

### Phase A - Add V7 package foundation
- Create `src/application/langgraph/retrieval_strategy/` with grouped subpackages and stable exports.
- Start with deterministic-first models and policies.

### Phase B - Deterministic selection only
- Implement:
  - signal extraction
  - deterministic strategy selection
  - strategy validation
  - plan building
  - plan validation
- Keep LLM selector disabled and unreferenced in live flow initially.

### Phase C - Tool-aware execution
- Extend `ToolRegistry` to expose specialized retrieval tools already present in the repo.
- Build plan execution only through `ToolRegistry`.
- Preserve fallback to `retrieve_chunks`.

### Phase D - Integrate explicit retrieval route first
- Update `RetrieveEvidenceNode` to use V7 selection/planning/execution.
- This is the lowest-risk first integration because it does not change QA generation behavior yet.

### Phase E - Integrate QA route via existing override seam
- Reuse `QuestionAnsweringWorkflow.context_override_chunks`.
- Let `AnswerQuestionNode` optionally retrieve via V7 first, then pass selected evidence through `AnswerQuestionTool`.
- Preserve current direct QA fallback if strategy flow is disabled or fails validation.

### Phase F - Integrate reflection retry
- Extend V6 retry path to request strategy-aware retries.
- Preserve initial evidence and merge with retry evidence via existing merger seam.

### Phase G - Trace, CLI, and evaluation
- Add serializable trace payloads for:
  - signals
  - decision
  - fallback
  - plan
  - execution summary
- Add CLI flags and display.
- Add evaluation metrics and cases.

## Recommended Constraints For Implementation
- Do not rewrite `RetrievalWorkflow`.
- Do not bypass `RetrieveChunksTool` / retrieval application tools.
- Do not call repositories or Qdrant from LangGraph.
- Prefer deterministic strategy selection as the live default.
- Treat optional LLM strategy selection as a validated enhancement behind config/CLI flags.
- Preserve existing V1-V6 routes and outputs when V7 is disabled.
