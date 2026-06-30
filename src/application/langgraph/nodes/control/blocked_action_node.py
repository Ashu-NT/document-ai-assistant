from __future__ import annotations

from src.application.langgraph.nodes.node_utils import extend_trace
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder

_BLOCKED_ACTION_RESPONSE = (
    "This request was blocked because it attempts to delete, reingest, or "
    "mutate the document corpus. Destructive corpus operations require an "
    "explicit supported workflow and approval."
)


class BlockedActionNode:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "blocked_action",
            route=state.get("route"),
        )
        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "unsafe_request_blocked": True,
                "blocked_reason": state.get("blocked_reason"),
                "blocked_terms": state.get("blocked_terms", []),
            },
        )
        return {
            "unsafe_request_blocked": bool(state.get("unsafe_request_blocked", False)),
            "response_text": state.get("guardrail_user_message")
            or _BLOCKED_ACTION_RESPONSE,
            "trace": extend_trace(state["trace"], trace_entry),
        }
