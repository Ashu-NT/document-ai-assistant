from __future__ import annotations

from src.application.langgraph.nodes.node_utils import extend_trace
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder

_HELP_TEXT = (
    "Supported commands:\n"
    "- list documents\n"
    "- open <document>\n"
    "- find document <document>\n"
    "- explore it\n"
    "- current document\n"
    "- clear document\n"
    "- help\n"
    "- exit"
)


class SessionCommandNode:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "session_command",
            route=state.get("route"),
        )
        route = state.get("route")
        patch: dict[str, object] = {}

        if route == "current_document":
            patch["response_text"] = _format_current_document(state)
        elif route == "clear_document":
            patch.update(
                {
                    "document_id": None,
                    "document_title": None,
                    "document_query": None,
                    "selected_document_id": None,
                    "selected_document_title": None,
                    "selected_document_file_name": None,
                    "pending_clarification": None,
                    "clarification_options": [],
                    "clarification_question": None,
                    "clarification_candidate_index": None,
                    "needs_clarification": False,
                    "clarification_message": None,
                    "response_text": "Cleared selected document.",
                }
            )
        elif route == "help":
            patch["help_text"] = _HELP_TEXT
            patch["response_text"] = _HELP_TEXT
        elif route == "exit":
            patch["should_exit"] = True
            patch["response_text"] = "Exiting document agent."
        else:
            patch["response_text"] = state.get("response_text") or "Request completed."

        trace_entry = self.recorder.finish_node(token, success=True)
        patch["trace"] = extend_trace(state["trace"], trace_entry)
        return patch


def _format_current_document(state: AgentState) -> str:
    title = state.get("selected_document_title") or state.get("document_title")
    document_id = state.get("selected_document_id") or state.get("document_id")
    file_name = state.get("selected_document_file_name")
    if not document_id:
        return "No document is currently selected."
    if file_name:
        return f"Current document: {title or document_id} ({file_name})."
    return f"Current document: {title or document_id}."
