from __future__ import annotations

from src.application.langgraph.nodes.node_utils import (
    extend_trace,
    format_document_options,
)
from src.application.langgraph.reflection.constants import REFLECTION_CLARIFICATION_KIND
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


class ClarifyRequestNode:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "clarify_request",
            route=state.get("route"),
        )
        response_text = self._build_response_text(state)
        patch = {
            "response_text": response_text,
            "trace": extend_trace(
                state["trace"],
                self.recorder.finish_node(token, success=True),
            ),
        }
        if state.get("route") == RouteType.CLARIFICATION_RESPONSE.value:
            patch.update(_resolve_clarification_response(state))
        elif state.get("clarification_options"):
            patch["pending_clarification"] = state.get("pending_clarification") or {
                "kind": "document_selection"
            }
            patch["clarification_question"] = (
                state.get("clarification_question")
                or "I found multiple matching documents. Which one do you mean?"
            )
            patch["needs_clarification"] = True
        return patch

    def _build_response_text(self, state: AgentState) -> str:
        if state.get("route") == RouteType.CLARIFICATION_RESPONSE.value:
            resolution_message = _resolve_clarification_message(state)
            if resolution_message is not None:
                return resolution_message
        if _is_reflection_clarification(state):
            return (
                state.get("clarification_message")
                or state.get("clarification_question")
                or "Please clarify your request."
            )
        if state.get("clarification_options"):
            return format_document_options(state["clarification_options"])
        return (
            state.get("clarification_message")
            or state.get("response_text")
            or "Please clarify your request."
        )


def _resolve_clarification_message(state: AgentState) -> str | None:
    if _is_reflection_clarification(state):
        options = state.get("clarification_options") or []
        candidate_index = state.get("clarification_candidate_index")
        if not isinstance(candidate_index, int):
            return state.get("clarification_message") or state.get("clarification_question")
        if candidate_index < 0 or candidate_index >= len(options):
            return state.get("clarification_message") or state.get("clarification_question")
        option = options[candidate_index]
        label = option.get("label") if isinstance(option, dict) else None
        return f"Clarification noted: {label or candidate_index + 1}."

    options = state.get("clarification_options") or []
    if not options:
        return "There is no pending clarification to resolve."

    candidate_index = state.get("clarification_candidate_index")
    if not isinstance(candidate_index, int):
        return format_document_options(options)

    if candidate_index < 0 or candidate_index >= len(options):
        return (
            "That option number is out of range.\n"
            f"{format_document_options(options)}"
        )

    option = options[candidate_index]
    title = (
        option.get("display_name")
        or option.get("title")
        or option.get("file_name")
        or option.get("document_id")
    )
    return f"Selected document: {title}."


def _resolve_clarification_response(state: AgentState) -> dict[str, object]:
    if _is_reflection_clarification(state):
        return _resolve_reflection_clarification_response(state)

    options = state.get("clarification_options") or []
    candidate_index = state.get("clarification_candidate_index")
    if not options or not isinstance(candidate_index, int):
        return {
            "needs_clarification": False,
            "pending_clarification": None,
            "clarification_question": None,
            "clarification_candidate_index": None,
        }

    if candidate_index < 0 or candidate_index >= len(options):
        return {
            "needs_clarification": True,
            "pending_clarification": state.get("pending_clarification"),
            "clarification_question": state.get("clarification_question"),
            "clarification_candidate_index": None,
        }

    option = options[candidate_index]
    return {
        "document_id": option.get("document_id"),
        "document_title": option.get("display_name") or option.get("title"),
        "selected_document_id": option.get("document_id"),
        "selected_document_title": option.get("display_name") or option.get("title"),
        "selected_document_file_name": option.get("file_name"),
        "needs_clarification": False,
        "pending_clarification": None,
        "clarification_options": [],
        "clarification_question": None,
        "clarification_candidate_index": None,
        "clarification_message": None,
    }


def _resolve_reflection_clarification_response(state: AgentState) -> dict[str, object]:
    pending = state.get("pending_clarification") or {}
    options = state.get("clarification_options") or []
    candidate_index = state.get("clarification_candidate_index")
    original_user_input = (
        pending.get("original_user_input")
        or (pending.get("resume_payload") or {}).get("original_user_input")
        or state.get("question")
        or state.get("user_input")
    )
    if not isinstance(candidate_index, int) or candidate_index < 0 or candidate_index >= len(options):
        return {
            "needs_clarification": True,
            "pending_clarification": pending,
            "clarification_options": options,
            "clarification_question": state.get("clarification_question"),
            "clarification_candidate_index": None,
            "clarification_message": state.get("clarification_message"),
        }
    option = options[candidate_index]
    selected_label = (
        option.get("value")
        if isinstance(option, dict) and option.get("value")
        else option.get("label")
        if isinstance(option, dict)
        else str(candidate_index + 1)
    )
    resumed_question = (
        f"{original_user_input} User clarified: {selected_label}."
    ).strip()
    resume_route = pending.get("resume_route") or RouteType.ANSWER_QUESTION.value
    return {
        "route": resume_route,
        "question": resumed_question,
        "user_input": resumed_question,
        "needs_clarification": False,
        "pending_clarification": None,
        "clarification_options": [],
        "clarification_question": None,
        "clarification_candidate_index": None,
        "clarification_message": None,
        "response_text": None,
    }


def _is_reflection_clarification(state: AgentState) -> bool:
    pending = state.get("pending_clarification")
    return isinstance(pending, dict) and pending.get("kind") == REFLECTION_CLARIFICATION_KIND
