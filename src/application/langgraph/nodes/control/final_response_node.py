from __future__ import annotations

from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.langgraph.nodes.node_utils import extend_trace


class FinalResponseNode:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "final_response",
            route=state.get("route"),
        )
        response_text = state.get("response_text") or "Request completed."
        trace_entry = self.recorder.finish_node(token, success=state.get("error") is None)
        return {
            "response_text": response_text,
            "trace": extend_trace(state["trace"], trace_entry),
        }
