from __future__ import annotations

from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.langgraph.nodes.node_utils import extend_trace


class ErrorHandlerNode:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "error_handler",
            route=state.get("route"),
        )
        error = state.get("error") or {}
        response_text = error.get("message") or "The request could not be completed."
        trace_entry = self.recorder.finish_node(
            token,
            success=False,
            error_code=error.get("error_code"),
            diagnostics=error.get("diagnostics", {}),
        )
        return {
            "response_text": response_text,
            "trace": extend_trace(state["trace"], trace_entry),
        }
