from __future__ import annotations

from typing import Any

from src.application.langgraph.common import GraphError, serialize_graph_value
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import build_error, extend_trace
from src.application.langgraph.reflection import (
    EvidenceMerger,
    RetryQueryBuilder,
    RetrievalRetryPolicy,
)
from src.application.langgraph.state import AgentState
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
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.evidence_merger = evidence_merger or EvidenceMerger()
        self.retry_query_builder = retry_query_builder or RetryQueryBuilder()
        self.retry_policy = retry_policy or RetrievalRetryPolicy()
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "retry_retrieval",
            route=state.get("route"),
        )
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
            "trace": extend_trace(state["trace"], trace_entry),
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
