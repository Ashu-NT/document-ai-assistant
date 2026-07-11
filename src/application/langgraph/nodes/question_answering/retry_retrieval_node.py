from __future__ import annotations

from typing import Any

from src.application.langgraph.common import (
    GraphError,
    resolve_state_response_text,
    serialize_graph_value,
)
from src.application.langgraph.common.answer_intent_resolver import (
    resolve_answer_intent,
)
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    deduplicate_identifiers,
    deserialize_identifiers,
    extend_trace,
    extract_identifiers_from_step_results,
)
from src.application.langgraph.nodes.question_answering.mappers.retrieved_chunk_state_mapper import (
    dict_to_chunk,
)
from src.application.langgraph.retrieval_strategy import (
    RetrievalContext,
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
    StrategyRetryPolicy,
)
from src.application.langgraph.retrieval_strategy.services.retrieval_strategy_state_adapter import (
    advisor_proposal_from_state,
    execution_result_to_tool_result,
    requested_strategy_from_state,
    strategy_patch as build_strategy_patch,
)
from src.application.langgraph.reflection import (
    EvidenceMerger,
    RetryQueryBuilder,
    RetrievalRetryPolicy,
)
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.question_answering import AnswerQuestionRequest
from src.application.tools.retrieval import RetrieveChunksRequest


class RetryRetrievalNode:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        evidence_merger: EvidenceMerger | None = None,
        retry_query_builder: RetryQueryBuilder | None = None,
        retry_policy: RetrievalRetryPolicy | None = None,
        retrieval_strategy_service: RetrievalStrategyService | None = None,
        retrieval_plan_executor: RetrievalPlanExecutor | None = None,
        retrieval_strategy_policy: RetrievalStrategyPolicy | None = None,
        strategy_retry_policy: StrategyRetryPolicy | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.evidence_merger = evidence_merger or EvidenceMerger()
        self.retry_query_builder = retry_query_builder or RetryQueryBuilder()
        self.retry_policy = retry_policy or RetrievalRetryPolicy()
        self.retrieval_strategy_service = retrieval_strategy_service
        self.retrieval_plan_executor = retrieval_plan_executor
        self.retrieval_strategy_policy = (
            retrieval_strategy_policy or RetrievalStrategyPolicy()
        )
        self.strategy_retry_policy = strategy_retry_policy or StrategyRetryPolicy()
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "retry_retrieval",
            route=state.get("route"),
        )
        if state.get("route") == RouteType.DEEP_RESEARCH.value:
            trace_entry = self.recorder.finish_node(
                token,
                success=True,
                diagnostics={"skipped": "deep_research"},
            )
            return {
                "response_text": resolve_state_response_text(state)
                or state.get("response_text"),
                "trace": extend_trace(state["trace"], trace_entry),
            }
        try:
            retrieve_tool = self.tool_registry.require("retrieve_chunks")
            answer_tool = self.tool_registry.require("answer_question")
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

        reflection_result = state.get("reflection_result") or {}
        decision = (reflection_result.get("decision") or {}) if isinstance(reflection_result, dict) else {}
        reason = str(decision.get("reason") or "Reflection requested a retrieval retry.")
        retry_query = state.get("retry_query")
        if not retry_query:
            retry_plan = self.retry_query_builder.build(
                original_user_question=state.get("question") or state["user_input"],
                answer_intent=_extract_answer_intent(state),
                selected_document_id=state.get("selected_document_id")
                or state.get("document_id"),
                reflection_decision=_decision_from_state(decision, reason),
                top_k=self._retry_top_k(state.get("top_k")),
            )
            retry_query = retry_plan.retry_query
        retry_top_k = self._retry_top_k(state.get("top_k"))
        retry_result = None
        resolved_identifiers = deserialize_identifiers(state.get("resolved_identifiers"))
        existing_structured_entities = state.get("resolved_structured_entities")
        resolved_structured_entities = list(existing_structured_entities) if isinstance(
            existing_structured_entities, list
        ) else []
        strategy_patch: dict[str, object] = {}
        if (
            state.get("retrieval_strategy_enabled")
            and self.retrieval_strategy_policy.enabled
            and self.retrieval_strategy_service is not None
            and self.retrieval_plan_executor is not None
        ):
            recommended_strategies = self.strategy_retry_policy.recommend(
                retry_reason=reason,
                retry_query=retry_query,
                initial_primary_strategy=_current_primary_strategy(state),
            )
            strategy_context = RetrievalContext(
                query_text=retry_query,
                route=state.get("route"),
                document_id=state.get("selected_document_id") or state.get("document_id"),
                selected_document_id=state.get("selected_document_id"),
                document_title=state.get("document_title"),
                selected_document_title=state.get("selected_document_title"),
                top_k=retry_top_k,
                answer_intent=_extract_answer_intent(state),
                retry_reason=reason,
                retry_query=retry_query,
                requested_strategy=recommended_strategies[0]
                if len(recommended_strategies) == 1
                else requested_strategy_from_state(state),
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
                resolved_identifiers = deduplicate_identifiers(
                    [
                        *resolved_identifiers,
                        *extract_identifiers_from_step_results(
                            execution_result.step_results
                        ),
                    ]
                )
                retry_result = execution_result_to_tool_result(
                    execution_result,
                    tool_name="retry_retrieval",
                    description="LangGraph retrieval-strategy retry execution result.",
                    success_message="Retry evidence retrieved successfully.",
                    failure_message="Retry retrieval strategy execution failed.",
                )
            except Exception as exc:
                strategy_patch = {
                    "retrieval_strategy_errors": [str(exc)],
                }

        if retry_result is None:
            retry_result = retrieve_tool.run(
                RetrieveChunksRequest(
                    query_text=retry_query,
                    document_id=state.get("selected_document_id") or state.get("document_id"),
                    top_k=retry_top_k,
                )
            )
        if not retry_result.success:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code=retry_result.error_code,
                diagnostics=retry_result.diagnostics,
            )
            return {
                "reflection_decision": "FAIL",
                "response_text": "I could not gather better evidence on retry.",
                "trace": extend_trace(state["trace"], trace_entry),
            }

        retry_data = retry_result.data or {}
        retry_chunks = list(retry_data.get("context_chunks", []) or [])
        initial_chunks = [dict_to_chunk(item) for item in state.get("initial_context_chunks", [])]
        merged_chunks, merge_diagnostics = self.evidence_merger.merge(
            initial_chunks=initial_chunks,
            retry_chunks=retry_chunks,
            policy=self.retry_policy,
            document_id=state.get("selected_document_id") or state.get("document_id"),
        )
        regenerated = answer_tool.run(
            AnswerQuestionRequest(
                question=state.get("question") or state["user_input"],
                document_id=state.get("selected_document_id") or state.get("document_id"),
                top_k=state.get("top_k"),
                allow_answer_generation=state["allow_answer_generation"],
                include_context=state["include_context"],
                require_citations=True,
                context_override_chunks=merged_chunks,
                retry_query=retry_query,
                resolved_identifiers=resolved_identifiers,
                resolved_structured_entities=resolved_structured_entities,
            )
        )
        tool_results = dict(state["tool_results"])
        tool_results["retry_retrieval"] = serialize_graph_value(
            {
                "success": retry_result.success,
                "data": retry_data,
                "diagnostics": retry_result.diagnostics,
            }
        )
        if regenerated.success:
            tool_results["answer_question"] = serialize_graph_value(
                {
                    "success": regenerated.success,
                    "data": regenerated.data,
                    "diagnostics": regenerated.diagnostics,
                }
            )
        trace_entry = self.recorder.finish_node(
            token,
            success=regenerated.success,
            diagnostics=merge_diagnostics,
        )
        patch = {
            "tool_results": tool_results,
            "retrieval_retry_count": int(state.get("retrieval_retry_count", 0)) + 1,
            "retry_query": retry_query,
            "retry_context_chunks": serialize_graph_value(retry_chunks),
            "merged_context_chunks": serialize_graph_value(merged_chunks),
            "merged_chunk_ids": [chunk.chunk_id for chunk in merged_chunks],
            "resolved_identifiers": serialize_graph_value(resolved_identifiers),
            "resolved_structured_entities": serialize_graph_value(
                resolved_structured_entities
            ),
            "trace": extend_trace(state["trace"], trace_entry),
            **strategy_patch,
        }
        if regenerated.success:
            qa_result = regenerated.data
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
            patch["reflection_decision"] = None
            patch["reflection_result"] = None
            patch["reflection_score"] = None
            return patch

        patch["response_text"] = "I could not regenerate a grounded answer after retry."
        patch["reflection_decision"] = "FAIL"
        return patch

    def _retry_top_k(self, current_top_k: int | None) -> int:
        base = current_top_k or 5
        if self.retry_policy.increase_top_k_on_retry:
            return base + self.retry_policy.retry_top_k_increment
        return base


def _decision_from_state(
    payload: dict[str, Any],
    reason: str,
):
    from src.application.langgraph.reflection.models import (
        ReflectionDecision,
        ReflectionDecisionType,
    )

    decision_value = str(payload.get("decision") or "RETRIEVE_AGAIN").upper()
    try:
        decision_type = ReflectionDecisionType(decision_value)
    except ValueError:
        decision_type = ReflectionDecisionType.RETRIEVE_AGAIN
    return ReflectionDecision(
        decision=decision_type,
        confidence=float(payload.get("confidence") or 0.0),
        reason=reason,
        retry_query=str(payload.get("retry_query") or "").strip() or None,
        clarification_question=str(payload.get("clarification_question") or "").strip()
        or None,
        missing_information=[
            str(item).strip()
            for item in (payload.get("missing_information") or [])
            if str(item).strip()
        ],
    )


def _extract_answer_intent(state: AgentState) -> str | None:
    return resolve_answer_intent(
        (state.get("tool_results", {}).get("answer_question") or {}).get("data")
    )


def _current_primary_strategy(state: AgentState):
    decision = state.get("retrieval_strategy_decision")
    if not isinstance(decision, dict):
        return None
    value = decision.get("primary_strategy")
    try:
        from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy

        return RetrievalStrategy(str(value))
    except Exception:
        return None
