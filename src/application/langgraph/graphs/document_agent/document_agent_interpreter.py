from __future__ import annotations

from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.state import AgentState, build_agent_state


def build_initial_state(
    *,
    user_input: str,
    document_id: str | None,
    document_query: str | None,
    session_id: str | None,
    allow_answer_generation: bool,
    include_context: bool,
    llm_planning_enabled: bool,
    show_plan: bool,
    show_raw_plan: bool,
    deep_research_enabled: bool,
    llm_research_planning_enabled: bool,
    show_research_plan: bool,
    show_research_trace: bool,
    reflection_enabled: bool,
    show_reflection: bool,
    retrieval_strategy_enabled: bool,
    llm_retrieval_strategy_enabled: bool,
    show_retrieval_strategy: bool,
    requested_retrieval_strategy: str | None,
    top_k: int | None,
    conversation_id: str | None,
    memory: ConversationMemory | None,
) -> AgentState:
    initial_state = build_agent_state(
        user_input=user_input,
        document_id=document_id,
        document_query=document_query,
        allow_answer_generation=allow_answer_generation,
        include_context=include_context,
        llm_planning_enabled=llm_planning_enabled,
        show_plan=show_plan,
        show_raw_plan=show_raw_plan,
        deep_research_enabled=deep_research_enabled,
        llm_research_planning_enabled=llm_research_planning_enabled,
        show_research_plan=show_research_plan,
        show_research_trace=show_research_trace,
        reflection_enabled=reflection_enabled,
        show_reflection=show_reflection,
        retrieval_strategy_enabled=retrieval_strategy_enabled,
        llm_retrieval_strategy_enabled=llm_retrieval_strategy_enabled,
        show_retrieval_strategy=show_retrieval_strategy,
        requested_retrieval_strategy=requested_retrieval_strategy,
        top_k=top_k,
        conversation_id=conversation_id,
        session_id=session_id,
        history=[],
    )
    if memory is not None:
        session_snapshot = memory.load_session(initial_state["session_id"])
        initial_state["history"] = list(session_snapshot.get("history", []))
        initial_state["selected_document_id"] = session_snapshot.get(
            "selected_document_id"
        )
        initial_state["selected_document_title"] = session_snapshot.get(
            "selected_document_title"
        )
        initial_state["selected_document_file_name"] = session_snapshot.get(
            "selected_document_file_name"
        )
        initial_state["pending_clarification"] = session_snapshot.get(
            "pending_clarification"
        )
        initial_state["clarification_options"] = list(
            session_snapshot.get("clarification_options", [])
        )
        initial_state["clarification_question"] = session_snapshot.get(
            "clarification_question"
        )

    return initial_state
