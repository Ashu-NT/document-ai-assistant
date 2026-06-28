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
from src.application.tools.evaluation import RetrievalTraceRequest


class RetrievalTraceNode:
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
            "retrieval_trace",
            route=state.get("route"),
            tool_name="retrieval_trace",
        )
        try:
            tool = self.tool_registry.require("retrieval_trace")
        except GraphError as exc:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code="not_supported",
                diagnostics=exc.details,
            )
            return {
                "error": build_error(
                    message="Retrieval trace is not configured.",
                    error_code="not_supported",
                    diagnostics=exc.details,
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        query_text = state.get("question") or state["user_input"].strip()
        result = tool.run(
            RetrievalTraceRequest(
                query_text=query_text,
                document_id=state.get("document_id"),
                top_k=state.get("top_k") or 5,
            )
        )
        tool_results = dict(state["tool_results"])
        tool_results["retrieval_trace"] = serialize_tool_result(result)
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
            patch["response_text"] = (
                f"Retrieval trace ready at {data.get('trace_path') or 'memory'}."
            )
            return patch

        patch["error"] = build_error(
            message=result.message or "Retrieval trace failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics,
        )
        return patch
