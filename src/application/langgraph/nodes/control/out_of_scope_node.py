from __future__ import annotations

from src.application.langgraph.nodes.node_utils import extend_trace
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder

_DEFAULT_OUT_OF_SCOPE_RESPONSE = (
    "I’m focused on indexed technical documents. I can help you search manuals, "
    "datasheets, drawings, certificates, and reports, or answer grounded questions "
    "about the selected document."
)


class OutOfScopeNode:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "out_of_scope",
            route=state.get("route"),
        )
        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "guardrail_decision": state.get("guardrail_decision"),
                "guardrail_trace_id": state.get("guardrail_trace_id"),
            },
        )
        return {
            "response_text": state.get("guardrail_user_message")
            or _DEFAULT_OUT_OF_SCOPE_RESPONSE,
            "trace": extend_trace(state["trace"], trace_entry),
        }
