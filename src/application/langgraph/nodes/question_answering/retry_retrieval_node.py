from __future__ import annotations

from dataclasses import asdict
from typing import Any

from src.application.langgraph.common import (
    GraphError,
    resolve_state_response_text,
    serialize_graph_value,
)
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    deduplicate_identifiers,
    deserialize_identifiers,
    extend_trace,
    extract_identifiers_from_step_results,
)
from src.application.langgraph.retrieval_strategy import (
    CLI_RETRIEVAL_STRATEGY_ALIASES,
    RetrievalContext,
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
    StrategyRetryPolicy,
)
from src.application.langgraph.reflection import (
    EvidenceMerger,
    RetryQueryBuilder,
    RetrievalRetryPolicy,
)
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorProposal,
)
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.question_answering import AnswerQuestionRequest
from src.application.tools.retrieval import RetrieveChunksRequest
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


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
                else _requested_strategy_from_state(state),
                use_llm_selector=bool(state.get("llm_retrieval_strategy_enabled")),
                strategy_advisor_proposal=_advisor_proposal_from_state(state),
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
                strategy_patch = _strategy_patch(
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
                retry_result = _execution_result_to_tool_result(execution_result)
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
        initial_chunks = [_dict_to_chunk(item) for item in state.get("initial_context_chunks", [])]
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
            "trace": extend_trace(state["trace"], trace_entry),
            **strategy_patch,
        }
        if regenerated.success:
            qa_result = regenerated.data
            patch["response_text"] = getattr(qa_result, "answer_text", None) or getattr(
                qa_result,
                "safe_user_message",
                None,
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
    answer_payload = (state.get("tool_results", {}).get("answer_question") or {}).get("data")
    if isinstance(answer_payload, dict):
        value = answer_payload.get("answer_intent")
        if isinstance(value, str) and value:
            return value
        diagnostics = answer_payload.get("diagnostics")
        if isinstance(diagnostics, dict):
            diag_value = diagnostics.get("answer_intent")
            if isinstance(diag_value, str) and diag_value:
                return diag_value
    return None


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


def _requested_strategy_from_state(state: AgentState):
    raw_value = state.get("requested_retrieval_strategy")
    if not isinstance(raw_value, str) or not raw_value:
        return None
    return CLI_RETRIEVAL_STRATEGY_ALIASES.get(raw_value.strip().lower())


def _advisor_proposal_from_state(state: AgentState) -> StrategyAdvisorProposal | None:
    payload = state.get("strategy_advisor_result")
    if not isinstance(payload, dict):
        return None
    proposal = payload.get("proposal")
    if not isinstance(proposal, dict):
        return None
    return StrategyAdvisorProposal.from_dict(proposal)


def _strategy_patch(
    *,
    strategy_result,
    execution_result,
) -> dict[str, object]:
    decision = strategy_result.decision
    return {
        "retrieval_strategy_decision": serialize_graph_value(asdict(decision)),
        "retrieval_plan": serialize_graph_value(strategy_result.plan.to_dict()),
        "retrieval_execution_result": serialize_graph_value(
            execution_result.to_dict()
        ),
        "retrieval_strategy_trace": serialize_graph_value(asdict(strategy_result.trace)),
        "selected_retrieval_strategies": [
            strategy.value for strategy in decision.selected_strategies
        ],
        "retrieval_strategy_errors": list(execution_result.errors),
    }


def _execution_result_to_tool_result(execution_result):
    from src.application.tools.common import ToolMetadata, ToolResult
    from src.domain.retrieval.citation import Citation

    citations = [
        chunk.citation
        for chunk in execution_result.evidence_chunks
        if isinstance(chunk.citation, Citation)
    ]
    metadata = ToolMetadata(
        tool_name="retry_retrieval",
        category="retrieval",
        description="LangGraph retrieval-strategy retry execution result.",
        mutates_state=False,
        supports_trace=True,
    )
    return ToolResult(
        success=execution_result.success,
        message=(
            "Retry evidence retrieved successfully."
            if execution_result.success
            else "Retry retrieval strategy execution failed."
        ),
        data={
            "chunks": execution_result.evidence_chunks,
            "context_chunks": execution_result.evidence_chunks,
            "citations": citations,
            "retrieval_execution_result": execution_result,
        },
        error_code=(
            None
            if execution_result.success
            else execution_result.errors[0]
            if execution_result.errors
            else "retrieval_strategy_failed"
        ),
        diagnostics=dict(execution_result.diagnostics),
        metadata=metadata,
    )


def _dict_to_chunk(payload: dict[str, Any]) -> RetrievedChunk:
    citation_payload = payload.get("citation")
    citation = _dict_to_citation(citation_payload) if isinstance(citation_payload, dict) else None
    return RetrievedChunk(
        chunk_id=str(payload.get("chunk_id") or ""),
        document_id=str(payload.get("document_id") or ""),
        content=str(payload.get("content") or ""),
        score=float(payload.get("score") or 0.0),
        retrieval_source=str(payload.get("retrieval_source") or "merged"),
        chunk_type=_chunk_type_from_value(payload.get("chunk_type")),
        section_id=str(payload.get("section_id") or "") or None,
        section_path=[
            str(part) for part in (payload.get("section_path") or []) if str(part)
        ],
        source=_dict_to_source(payload.get("source")),
        citation=citation,
        metadata={
            str(key): str(value)
            for key, value in (payload.get("metadata") or {}).items()
        }
        if isinstance(payload.get("metadata"), dict)
        else {},
    )


def _dict_to_source(payload: Any) -> SourceLocation:
    if not isinstance(payload, dict):
        return SourceLocation()
    page_start = payload.get("page_start")
    page_end = payload.get("page_end")
    return SourceLocation(
        page_start=int(page_start) if isinstance(page_start, int) else None,
        page_end=int(page_end) if isinstance(page_end, int) else None,
    )


def _dict_to_citation(payload: dict[str, Any]) -> Citation:
    source = _dict_to_source(payload.get("source"))
    return Citation(
        citation_id=str(payload.get("citation_id") or ""),
        document_id=str(payload.get("document_id") or ""),
        chunk_id=str(payload.get("chunk_id") or "") or None,
        section_id=str(payload.get("section_id") or "") or None,
        document_name=str(payload.get("document_name") or "") or None,
        section_title=str(payload.get("section_title") or "") or None,
        source=source,
    )


def _chunk_type_from_value(value: Any) -> ChunkType:
    try:
        return ChunkType(str(value))
    except Exception:
        return ChunkType.UNKNOWN
