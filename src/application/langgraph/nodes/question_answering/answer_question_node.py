from __future__ import annotations

from src.application.langgraph.common import GraphError
from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.common.answer_intent_resolver import (
    resolve_answer_intent,
)
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    deduplicate_identifiers,
    deserialize_identifiers,
    extract_identifiers_from_step_results,
    extend_trace,
    resolve_selected_document,
    serialize_tool_result,
)
from src.application.langgraph.retrieval_strategy import (
    RetrievalContext,
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
    advisor_proposal_from_state,
    requested_strategy_from_state,
    strategy_patch as build_strategy_patch,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.question_answering import AnswerQuestionRequest


class AnswerQuestionNode:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        retrieval_strategy_service: RetrievalStrategyService | None = None,
        retrieval_plan_executor: RetrievalPlanExecutor | None = None,
        retrieval_strategy_policy: RetrievalStrategyPolicy | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.retrieval_strategy_service = retrieval_strategy_service
        self.retrieval_plan_executor = retrieval_plan_executor
        self.retrieval_strategy_policy = (
            retrieval_strategy_policy or RetrievalStrategyPolicy()
        )
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "answer_question",
            route=state.get("route"),
            tool_name="answer_question",
        )
        try:
            tool = self.tool_registry.require("answer_question")
        except GraphError as exc:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code=exc.error_code,
                diagnostics=exc.details,
            )
            return {
                "error": build_error(
                    message=exc.message,
                    error_code=exc.error_code,
                    diagnostics=exc.details,
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        question = state.get("question") or state["user_input"].strip()
        resolved_document_id, _ = resolve_selected_document(state)
        context_override_chunks = None
        resolved_identifiers = deserialize_identifiers(
            state.get("resolved_identifiers")
        )
        existing_structured_entities = state.get("resolved_structured_entities")
        resolved_structured_entities = (
            list(existing_structured_entities)
            if isinstance(existing_structured_entities, list)
            else []
        )
        strategy_patch: dict[str, object] = {}
        if (
            state.get("retrieval_strategy_enabled")
            and self.retrieval_strategy_policy.enabled
            and self.retrieval_strategy_service is not None
            and self.retrieval_plan_executor is not None
        ):
            strategy_context = RetrievalContext(
                query_text=question,
                route=state.get("route"),
                document_id=resolved_document_id,
                selected_document_id=state.get("selected_document_id"),
                document_title=state.get("document_title"),
                selected_document_title=state.get("selected_document_title"),
                top_k=state.get("top_k") or self.retrieval_strategy_policy.default_top_k,
                answer_intent=resolve_answer_intent(
                    (state.get("tool_results", {}).get("answer_question") or {}).get("data")
                ),
                requested_strategy=requested_strategy_from_state(state),
                use_llm_selector=bool(state.get("llm_retrieval_strategy_enabled")),
                strategy_advisor_proposal=advisor_proposal_from_state(state),
            )
            try:
                strategy_result = self.retrieval_strategy_service.select_and_plan(
                    strategy_context,
                    tool_registry=self.tool_registry,
                )
                execution_result = self.retrieval_plan_executor.execute(
                    strategy_result.plan,
                    tool_registry=self.tool_registry,
                    max_chunks=self.retrieval_strategy_policy.max_merged_chunks,
                )
                strategy_patch = build_strategy_patch(
                    strategy_result=strategy_result,
                    execution_result=execution_result,
                )
                if execution_result.evidence_chunks:
                    context_override_chunks = execution_result.evidence_chunks
                resolved_identifiers = deduplicate_identifiers(
                    [
                        *resolved_identifiers,
                        *extract_identifiers_from_step_results(
                            execution_result.step_results
                        ),
                    ]
                )
            except Exception as exc:
                strategy_patch = {
                    "retrieval_strategy_errors": [str(exc)],
                }
        result = tool.run(
            AnswerQuestionRequest(
                question=question,
                document_id=resolved_document_id,
                top_k=state.get("top_k"),
                allow_answer_generation=state["allow_answer_generation"],
                include_context=state["include_context"],
                require_citations=True,
                context_override_chunks=context_override_chunks,
                resolved_identifiers=resolved_identifiers,
                resolved_structured_entities=resolved_structured_entities,
            )
        )
        tool_results = dict(state["tool_results"])
        tool_results["answer_question"] = serialize_tool_result(result)
        trace_entry = self.recorder.finish_node(
            token,
            success=result.success,
            error_code=result.error_code,
            diagnostics={
                **dict(result.diagnostics or {}),
                "retrieval_strategy": strategy_patch.get("retrieval_strategy_decision"),
            },
        )
        patch = {
            "tool_results": tool_results,
            "trace": extend_trace(state["trace"], trace_entry),
            "resolved_identifiers": serialize_graph_value(resolved_identifiers),
            "resolved_structured_entities": serialize_graph_value(
                resolved_structured_entities
            ),
            **strategy_patch,
        }
        if result.success:
            qa_result = result.data
            qa_identifiers = getattr(
                qa_result,
                "resolved_identifiers",
                resolved_identifiers,
            )
            qa_structured_entities = getattr(
                qa_result,
                "resolved_structured_entities",
                resolved_structured_entities,
            )
            patch["response_text"] = getattr(qa_result, "answer_text", None) or getattr(
                qa_result,
                "safe_user_message",
                None,
            )
            patch["resolved_identifiers"] = serialize_graph_value(qa_identifiers)
            patch["resolved_structured_entities"] = serialize_graph_value(
                qa_structured_entities
            )
            retrieval_result = getattr(qa_result, "retrieval_result", None)
            context_chunks = (
                getattr(retrieval_result, "final_chunks", [])
                if retrieval_result is not None
                else []
            )
            serialized_chunks = serialize_graph_value(context_chunks)
            patch["initial_context_chunks"] = serialized_chunks
            patch["merged_context_chunks"] = serialized_chunks
            patch["merged_chunk_ids"] = [
                str(chunk.get("chunk_id"))
                for chunk in serialized_chunks
                if isinstance(chunk, dict) and chunk.get("chunk_id")
            ]
            return patch

        patch["error"] = build_error(
            message=result.message or "Question answering failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics,
        )
        return patch
