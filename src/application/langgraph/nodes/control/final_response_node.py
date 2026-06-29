from __future__ import annotations

from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.langgraph.nodes.node_utils import extend_trace


class FinalResponseNode:
    def __init__(
        self,
        *,
        memory: ConversationMemory | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.memory = memory
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "final_response",
            route=state.get("route"),
        )
        if self.memory is not None:
            self.memory.save_session_state(
                session_id=state.get("session_id"),
                selected_document_id=state.get("selected_document_id"),
                selected_document_title=state.get("selected_document_title"),
                selected_document_file_name=state.get("selected_document_file_name"),
                pending_clarification=state.get("pending_clarification"),
                clarification_options=state.get("clarification_options"),
                clarification_question=state.get("clarification_question"),
            )
        response_text = state.get("response_text") or "Request completed."
        trace_entry = self.recorder.finish_node(token, success=state.get("error") is None)
        return {
            "response_text": response_text,
            "trace": extend_trace(state["trace"], trace_entry),
        }
