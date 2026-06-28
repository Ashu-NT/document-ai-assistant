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
from src.application.tools.documents import ListDocumentsRequest


class ListDocumentsNode:
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
            "list_documents",
            route=state.get("route"),
            tool_name="list_documents",
        )
        try:
            tool = self.tool_registry.require("list_documents")
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

        result = tool.run(ListDocumentsRequest())
        tool_results = dict(state["tool_results"])
        tool_results["list_documents"] = serialize_tool_result(result)
        rows = result.data or []
        trace_entry = self.recorder.finish_node(
            token,
            success=result.success,
            error_code=result.error_code,
            diagnostics=result.diagnostics,
        )
        patch = {
            "tool_results": tool_results,
            "response_text": result.message or f"Found {len(rows)} document(s).",
            "trace": extend_trace(state["trace"], trace_entry),
        }
        if not result.success:
            patch["error"] = build_error(
                message=result.message or "Failed to list documents.",
                error_code=result.error_code or "tool_failed",
                diagnostics=result.diagnostics,
            )
        return patch
