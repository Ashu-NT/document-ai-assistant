from __future__ import annotations

from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.langgraph.nodes.node_utils import extend_trace


class ClarifyRequestNode:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "clarify_request",
            route=state.get("route"),
        )
        response_text = (
            state.get("clarification_message")
            or state.get("response_text")
            or "Please clarify your request."
        )
        trace_entry = self.recorder.finish_node(token, success=True)
        return {
            "response_text": response_text,
            "trace": extend_trace(state["trace"], trace_entry),
        }
