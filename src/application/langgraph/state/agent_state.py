from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict):
    user_input: str
    normalized_input: str | None
    route: str | None
    document_query: str | None
    document_id: str | None
    document_title: str | None
    question: str | None
    allow_answer_generation: bool
    include_context: bool
    top_k: int | None
    tool_results: dict[str, Any]
    response_text: str | None
    error: dict[str, Any] | None
    needs_clarification: bool
    clarification_message: str | None
    trace: list[dict[str, Any]]
    conversation_id: str | None
    history: list[dict[str, Any]]


def build_agent_state(
    *,
    user_input: str,
    document_id: str | None = None,
    document_query: str | None = None,
    allow_answer_generation: bool = False,
    include_context: bool = False,
    top_k: int | None = None,
    conversation_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> AgentState:
    return AgentState(
        user_input=user_input,
        normalized_input=None,
        route=None,
        document_query=document_query,
        document_id=document_id,
        document_title=None,
        question=None,
        allow_answer_generation=allow_answer_generation,
        include_context=include_context,
        top_k=top_k,
        tool_results={},
        response_text=None,
        error=None,
        needs_clarification=False,
        clarification_message=None,
        trace=[],
        conversation_id=conversation_id,
        history=list(history or []),
    )
