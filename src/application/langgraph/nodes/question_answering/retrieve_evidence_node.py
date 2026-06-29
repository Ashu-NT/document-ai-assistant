from __future__ import annotations

from src.application.langgraph.common import GraphError
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    extend_trace,
    resolve_selected_document,
    serialize_tool_result,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.retrieval import RetrieveChunksRequest


class RetrieveEvidenceNode:
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
            "retrieve_evidence",
            route=state.get("route"),
            tool_name="retrieve_chunks",
        )
        try:
            tool = self.tool_registry.require("retrieve_chunks")
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

        query_text = state.get("question") or state["user_input"].strip()
        resolved_document_id, _ = resolve_selected_document(state)
        result = tool.run(
            RetrieveChunksRequest(
                query_text=query_text,
                document_id=resolved_document_id,
                top_k=state.get("top_k") or 5,
            )
        )
        tool_results = dict(state["tool_results"])
        tool_results["retrieve_evidence"] = serialize_tool_result(result)
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
            chunk_count = len(data.get("chunks", []))
            context_count = len(data.get("context_chunks", []))
            patch["response_text"] = (
                f"Retrieved {chunk_count} evidence chunk(s); "
                f"{context_count} chunk(s) after context assembly."
            )
            return patch

        patch["error"] = build_error(
            message=result.message or "Evidence retrieval failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics,
        )
        return patch
