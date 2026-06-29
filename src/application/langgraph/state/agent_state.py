from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict):
    user_input: str
    normalized_input: str | None
    route: str | None
    document_query: str | None
    document_id: str | None
    document_title: str | None
    selected_document_id: str | None
    selected_document_title: str | None
    selected_document_file_name: str | None
    question: str | None
    allow_answer_generation: bool
    include_context: bool
    top_k: int | None
    tool_results: dict[str, Any]
    response_text: str | None
    error: dict[str, Any] | None
    needs_clarification: bool
    clarification_message: str | None
    pending_clarification: dict[str, Any] | None
    clarification_options: list[dict[str, Any]]
    clarification_question: str | None
    clarification_candidate_index: int | None
    trace: list[dict[str, Any]]
    conversation_id: str | None
    session_id: str | None
    session_command: str | None
    history: list[dict[str, Any]]
    should_exit: bool
    help_text: str | None


def build_agent_state(
    *,
    user_input: str,
    document_id: str | None = None,
    document_query: str | None = None,
    allow_answer_generation: bool = False,
    include_context: bool = False,
    top_k: int | None = None,
    conversation_id: str | None = None,
    session_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
    selected_document_id: str | None = None,
    selected_document_title: str | None = None,
    selected_document_file_name: str | None = None,
    pending_clarification: dict[str, Any] | None = None,
    clarification_options: list[dict[str, Any]] | None = None,
    clarification_question: str | None = None,
) -> AgentState:
    effective_session_id = session_id or conversation_id
    return AgentState(
        user_input=user_input,
        normalized_input=None,
        route=None,
        document_query=document_query,
        document_id=document_id,
        document_title=None,
        selected_document_id=selected_document_id,
        selected_document_title=selected_document_title,
        selected_document_file_name=selected_document_file_name,
        question=None,
        allow_answer_generation=allow_answer_generation,
        include_context=include_context,
        top_k=top_k,
        tool_results={},
        response_text=None,
        error=None,
        needs_clarification=False,
        clarification_message=None,
        pending_clarification=pending_clarification,
        clarification_options=list(clarification_options or []),
        clarification_question=clarification_question,
        clarification_candidate_index=None,
        trace=[],
        conversation_id=conversation_id or effective_session_id,
        session_id=effective_session_id,
        session_command=None,
        history=list(history or []),
        should_exit=False,
        help_text=None,
    )
