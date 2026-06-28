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
from src.application.tools.exploration import ExploreDocumentRequest


class ExploreDocumentNode:
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
            "explore_document",
            route=state.get("route"),
            tool_name="explore_document",
        )
        if not state.get("document_id"):
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code="clarification_required",
            )
            return {
                "needs_clarification": True,
                "clarification_message": "Please specify which document you want to explore.",
                "trace": extend_trace(state["trace"], trace_entry),
            }

        try:
            tool = self.tool_registry.require("explore_document")
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

        result = tool.run(ExploreDocumentRequest(document_id=state["document_id"]))
        tool_results = dict(state["tool_results"])
        tool_results["explore_document"] = serialize_tool_result(result)
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
            exploration = result.data
            overview = getattr(exploration, "overview", None)
            title = getattr(overview, "title", None) or getattr(overview, "file_name", None)
            sections = len(getattr(exploration, "sections", []))
            tables = len(getattr(exploration, "tables", []))
            identifiers = len(getattr(exploration, "identifiers", []))
            patch["response_text"] = (
                f"{title} | sections={sections} | tables={tables} | identifiers={identifiers}"
            )
            patch["document_title"] = title
            return patch

        patch["error"] = build_error(
            message=result.message or "Document exploration failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics,
        )
        return patch
