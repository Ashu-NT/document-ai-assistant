from __future__ import annotations

from typing import Any

from src.application.langgraph.nodes.node_utils import build_error, extend_trace
from src.application.langgraph.research import ResearchService
from src.application.langgraph.research.services import ResearchStateMapper
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


class ResearchSummaryNode:
    def __init__(
        self,
        research_service: ResearchService,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.research_service = research_service
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict[str, Any]:
        token = self.recorder.start_node(
            "research_summary",
            route=state.get("route"),
        )
        result = ResearchStateMapper.result_from_state(state)
        if result is None or result.report is None:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code="research_report_missing",
            )
            return {
                "error": build_error(
                    message="Research summary could not be created because the research report was missing.",
                    error_code="research_report_missing",
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        response_text = self.research_service.report_builder.render_text(
            result.report,
            policy=self.research_service.synthesis_policy,
        )

        context_chunks = _build_context_chunks(state.get("research_evidence"))
        citations = _build_citations(state.get("research_evidence"))
        approved_chunk_ids = [
            str(chunk.get("chunk_id"))
            for chunk in context_chunks
            if isinstance(chunk, dict) and chunk.get("chunk_id")
        ]
        tool_results = dict(state.get("tool_results", {}))
        tool_results["answer_question"] = {
            "success": True,
            "message": "Deep research summary prepared.",
            "error_code": None,
            "diagnostics": {
                "answer_intent": _answer_intent(result.goal.goal_type.value),
            },
            "metadata": None,
            "data": {
                "route": "deep_research",
                "answer_text": response_text,
                "answer_intent": _answer_intent(result.goal.goal_type.value),
                "citations": citations,
                "approved_chunk_ids": approved_chunk_ids,
                "rejected_chunk_ids": [],
                "retrieval_result": {
                    "context_chunks": context_chunks,
                },
            },
        }
        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "citation_count": len(citations),
                "context_chunk_count": len(context_chunks),
            },
        )
        return {
            "response_text": response_text,
            "tool_results": tool_results,
            "trace": extend_trace(state["trace"], trace_entry),
        }


def _build_context_chunks(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    chunks: list[dict[str, Any]] = []
    seen_chunk_ids: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        chunk_id = str(item.get("chunk_id") or "").strip()
        if chunk_id and chunk_id in seen_chunk_ids:
            continue
        if chunk_id:
            seen_chunk_ids.add(chunk_id)
        chunks.append(
            {
                "chunk_id": item.get("chunk_id"),
                "document_id": item.get("document_id"),
                "document_title": item.get("document_title"),
                "section_path": list(item.get("section_path") or []),
                "chunk_type": item.get("chunk_type"),
                "score": item.get("score"),
                "content": item.get("content_excerpt"),
                "retrieval_source": item.get("source_tool"),
                "source": {
                    "page_start": item.get("page_start"),
                    "page_end": item.get("page_end"),
                },
            }
        )
    return chunks


def _build_citations(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    citations: list[dict[str, Any]] = []
    seen_chunk_ids: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        chunk_id = str(item.get("chunk_id") or "").strip()
        if chunk_id and chunk_id in seen_chunk_ids:
            continue
        if chunk_id:
            seen_chunk_ids.add(chunk_id)
        section_path = list(item.get("section_path") or [])
        citations.append(
            {
                "citation_id": f"research-citation-{index}",
                "chunk_id": item.get("chunk_id"),
                "document_id": item.get("document_id"),
                "document_name": item.get("document_title"),
                "section_title": section_path[-1] if section_path else None,
                "section_path": section_path,
                "page_start": item.get("page_start"),
                "page_end": item.get("page_end"),
            }
        )
    return citations


def _answer_intent(goal_type: str) -> str:
    if goal_type == "comparison":
        return "research_comparison"
    if goal_type == "checklist":
        return "research_checklist"
    if goal_type == "report":
        return "research_report"
    return "research_summary"
