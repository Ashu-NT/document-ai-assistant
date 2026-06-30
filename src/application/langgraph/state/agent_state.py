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
    llm_planning_enabled: bool
    show_plan: bool
    show_raw_plan: bool
    deep_research_enabled: bool
    llm_research_planning_enabled: bool
    show_research_plan: bool
    show_research_trace: bool
    reflection_enabled: bool
    show_reflection: bool
    retrieval_strategy_enabled: bool
    llm_retrieval_strategy_enabled: bool
    show_retrieval_strategy: bool
    requested_retrieval_strategy: str | None
    top_k: int | None
    reflection_attempts: int
    retrieval_retry_count: int
    reflection_result: dict[str, Any] | None
    reflection_decision: str | None
    reflection_score: float | None
    answer_quality: dict[str, Any] | None
    evidence_quality: dict[str, Any] | None
    retry_query: str | None
    retrieval_strategy_decision: dict[str, Any] | None
    retrieval_plan: dict[str, Any] | None
    retrieval_execution_result: dict[str, Any] | None
    retrieval_strategy_trace: dict[str, Any] | None
    selected_retrieval_strategies: list[str]
    retrieval_strategy_errors: list[str]
    initial_context_chunks: list[dict[str, Any]]
    retry_context_chunks: list[dict[str, Any]]
    merged_context_chunks: list[dict[str, Any]]
    merged_chunk_ids: list[str]
    reflection_trace: list[dict[str, Any]]
    tool_results: dict[str, Any]
    execution_plan: dict[str, Any] | None
    validated_plan: dict[str, Any] | None
    plan_steps: list[dict[str, Any]]
    plan_results: dict[str, Any]
    planning_source: str | None
    planning_errors: list[str]
    planning_warnings: list[str]
    raw_llm_plan: str | None
    plan_success: bool | None
    failed_plan_step: str | None
    research_goal: dict[str, Any] | None
    research_plan: dict[str, Any] | None
    research_task_results: list[dict[str, Any]]
    research_evidence: list[dict[str, Any]]
    research_gaps: list[dict[str, Any]]
    research_iterations: int
    research_synthesis: dict[str, Any] | None
    research_report: dict[str, Any] | None
    research_errors: list[str]
    research_trace: dict[str, Any] | None
    research_followup_pending: bool
    research_plan_source: str | None
    research_planning_errors: list[str]
    research_planning_warnings: list[str]
    raw_llm_research_plan: str | None
    research_result: dict[str, Any] | None
    response_text: str | None
    error: dict[str, Any] | None
    unsafe_request_blocked: bool
    blocked_reason: str | None
    blocked_terms: list[str]
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
    llm_planning_enabled: bool = False,
    show_plan: bool = False,
    show_raw_plan: bool = False,
    deep_research_enabled: bool = False,
    llm_research_planning_enabled: bool = False,
    show_research_plan: bool = False,
    show_research_trace: bool = False,
    reflection_enabled: bool = False,
    show_reflection: bool = False,
    retrieval_strategy_enabled: bool = False,
    llm_retrieval_strategy_enabled: bool = False,
    show_retrieval_strategy: bool = False,
    requested_retrieval_strategy: str | None = None,
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
        reflection_attempts=0,
        retrieval_retry_count=0,
        reflection_result=None,
        reflection_decision=None,
        reflection_score=None,
        answer_quality=None,
        evidence_quality=None,
        retry_query=None,
        retrieval_strategy_decision=None,
        retrieval_plan=None,
        retrieval_execution_result=None,
        retrieval_strategy_trace=None,
        selected_retrieval_strategies=[],
        retrieval_strategy_errors=[],
        initial_context_chunks=[],
        retry_context_chunks=[],
        merged_context_chunks=[],
        merged_chunk_ids=[],
        reflection_trace=[],
        tool_results={},
        execution_plan=None,
        validated_plan=None,
        plan_steps=[],
        plan_results={},
        planning_source=None,
        planning_errors=[],
        planning_warnings=[],
        raw_llm_plan=None,
        plan_success=None,
        failed_plan_step=None,
        research_goal=None,
        research_plan=None,
        research_task_results=[],
        research_evidence=[],
        research_gaps=[],
        research_iterations=0,
        research_synthesis=None,
        research_report=None,
        research_errors=[],
        research_trace=None,
        research_followup_pending=False,
        research_plan_source=None,
        research_planning_errors=[],
        research_planning_warnings=[],
        raw_llm_research_plan=None,
        research_result=None,
        response_text=None,
        error=None,
        unsafe_request_blocked=False,
        blocked_reason=None,
        blocked_terms=[],
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
