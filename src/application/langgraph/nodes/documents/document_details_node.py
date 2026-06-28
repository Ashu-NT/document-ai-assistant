from __future__ import annotations

from src.application.langgraph.common import GraphError
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    extend_trace,
    serialize_tool_result,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.documents import DocumentDetailsRequest


class DocumentDetailsNode:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "document_details",
            route=state.get("route"),
            tool_name="document_details",
        )
        if not state.get("document_id"):
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code="clarification_required",
            )
            return {
                "needs_clarification": True,
                "clarification_message": "Please specify which document you want details for.",
                "trace": extend_trace(state["trace"], trace_entry),
            }

        try:
            tool = self.tool_registry.require("document_details")
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

        result = tool.run(DocumentDetailsRequest(document_id=state["document_id"]))
        tool_results = dict(state["tool_results"])
        tool_results["document_details"] = serialize_tool_result(result)
        trace_entry = self.recorder.finish_node(
            token,
            success=result.success,
            error_code=result.error_code,
            diagnostics=result.diagnostics,
        )
        patch = {
            "tool_results": tool_results,
            "trace": extend_trace(state["trace"], trace_entry),
        }
        if result.success:
            data = result.data or {}
            patch["document_title"] = data.get("display_name") or data.get("title")
            patch["response_text"] = _format_document_details(data)
            return patch

        patch["error"] = build_error(
            message=result.message or "Document details could not be loaded.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics,
        )
        return patch


def _format_document_details(data: dict) -> str:
    title = data.get("display_name") or data.get("title") or data.get("document_id")
    document_type = data.get("document_type") or "unknown"
    page_count = data.get("page_count")
    chunk_count = data.get("chunk_count")
    return (
        f"{title} | type={document_type} | pages={page_count or '-'} | "
        f"chunks={chunk_count or 0}"
    )
