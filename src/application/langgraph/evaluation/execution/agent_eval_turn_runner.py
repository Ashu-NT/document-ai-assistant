from __future__ import annotations

from typing import Any

from src.application.langgraph.common import GraphResult, serialize_graph_value
from src.application.langgraph.common.value_coercion import optional_str
from src.application.langgraph.evaluation.models.agent_eval_result import AgentTurnResult
from src.application.langgraph.evaluation.models.agent_test_case import AgentTurnInput
from src.application.langgraph.evaluation.scoring.turn_result_extractors import (
    extract_context_document_ids,
    extract_plan_tool_names,
    extract_trace_tool_names,
    extract_turn_errors,
    research_plan_task_count,
    research_report_section_count,
    research_task_counts,
    resolve_blocked_reason,
    resolve_blocked_terms,
    resolve_unsafe_blocked_flag,
)


def run_turn(
    graph: Any,
    turn_input: AgentTurnInput,
    *,
    session_id: str,
    llm_planning_enabled_override: bool | None,
    deep_research_enabled_override: bool | None,
    llm_research_planning_enabled_override: bool | None,
    answer_generation_enabled_override: bool | None,
    retrieval_strategy_enabled_override: bool | None,
    llm_retrieval_strategy_enabled_override: bool | None,
    requested_retrieval_strategy_override: str | None,
) -> AgentTurnResult:
    requested_retrieval_strategy = (
        requested_retrieval_strategy_override
        if requested_retrieval_strategy_override is not None
        else turn_input.requested_retrieval_strategy
    )
    llm_retrieval_strategy_enabled = (
        llm_retrieval_strategy_enabled_override
        if llm_retrieval_strategy_enabled_override is not None
        else turn_input.llm_retrieval_strategy_enabled
    )
    retrieval_strategy_enabled = (
        retrieval_strategy_enabled_override
        if retrieval_strategy_enabled_override is not None
        else (
            turn_input.retrieval_strategy_enabled
            or requested_retrieval_strategy is not None
            or llm_retrieval_strategy_enabled
        )
    )
    deep_research_enabled = (
        deep_research_enabled_override
        if deep_research_enabled_override is not None
        else turn_input.deep_research_enabled
    )
    llm_research_planning_enabled = (
        llm_research_planning_enabled_override
        if llm_research_planning_enabled_override is not None
        else turn_input.llm_research_planning_enabled
    )
    result: GraphResult = graph.run(
        turn_input.user_input,
        document_id=turn_input.document_id,
        document_query=turn_input.document,
        session_id=session_id,
        allow_answer_generation=(
            answer_generation_enabled_override
            if answer_generation_enabled_override is not None
            else turn_input.allow_answer_generation
        ),
        include_context=turn_input.show_context,
        llm_planning_enabled=(
            llm_planning_enabled_override
            if llm_planning_enabled_override is not None
            else turn_input.llm_planning_enabled
        ),
        deep_research_enabled=deep_research_enabled,
        llm_research_planning_enabled=llm_research_planning_enabled,
        retrieval_strategy_enabled=retrieval_strategy_enabled,
        llm_retrieval_strategy_enabled=llm_retrieval_strategy_enabled,
        requested_retrieval_strategy=requested_retrieval_strategy,
        show_retrieval_strategy=turn_input.show_retrieval_strategy,
        show_plan=turn_input.show_plan,
        show_research_plan=turn_input.show_research_plan,
        show_research_trace=turn_input.show_research_trace,
    )
    data = result.data or {}
    retrieval_strategy_decision = data.get("retrieval_strategy_decision")
    retrieval_strategy_primary = None
    retrieval_strategy_secondary: list[str] = []
    if isinstance(retrieval_strategy_decision, dict):
        primary = retrieval_strategy_decision.get("primary_strategy")
        if isinstance(primary, str) and primary:
            retrieval_strategy_primary = primary
        secondaries = retrieval_strategy_decision.get("secondary_strategies")
        if isinstance(secondaries, list):
            retrieval_strategy_secondary = [
                str(item)
                for item in secondaries
                if isinstance(item, str) and item
            ]
    research_plan = data.get("research_plan")
    research_task_results = data.get("research_task_results")
    research_gaps = data.get("research_gaps")
    research_report = data.get("research_report")
    research_trace = data.get("research_trace")
    citations = data.get("citations")
    research_task_count, research_task_success_count = research_task_counts(
        research_task_results
    )
    retrieval_strategy_trace = data.get("retrieval_strategy_trace")
    selected_document_id = optional_str(
        data.get("selected_document_id")
    ) or optional_str(data.get("document_id"))
    selected_document_title = optional_str(
        data.get("selected_document_title")
    ) or optional_str(data.get("document_title"))
    return AgentTurnResult(
        user_input=turn_input.user_input,
        route=result.route,
        success=result.success,
        response_text=optional_str(data.get("answer")) or result.response_text,
        selected_document_id=selected_document_id,
        selected_document_title=selected_document_title,
        tool_names=extract_trace_tool_names(result.trace or []),
        plan_tool_names=extract_plan_tool_names(data),
        context_document_ids=extract_context_document_ids(data),
        retrieval_strategy_primary=retrieval_strategy_primary,
        retrieval_strategy_secondary=retrieval_strategy_secondary,
        retrieval_strategy_trace_present=isinstance(
            retrieval_strategy_trace,
            dict,
        ),
        retrieval_strategy_fallback_used=bool(
            isinstance(retrieval_strategy_trace, dict)
            and retrieval_strategy_trace.get("fallback_reason")
        ),
        retrieval_strategy_enabled=retrieval_strategy_enabled,
        research_plan_present=isinstance(research_plan, dict),
        research_plan_task_count=research_plan_task_count(research_plan),
        research_plan_source=optional_str(data.get("research_plan_source")),
        research_task_count=research_task_count,
        research_task_success_count=research_task_success_count,
        research_gap_count=len(research_gaps) if isinstance(research_gaps, list) else 0,
        research_report_present=isinstance(research_report, dict),
        research_report_section_count=research_report_section_count(
            research_report
        ),
        research_citation_count=len(citations) if isinstance(citations, list) else 0,
        research_trace_present=isinstance(research_trace, dict),
        diagnostics=serialize_graph_value(
            {
                "error_code": result.error_code,
                "graph_diagnostics": result.diagnostics or {},
                "unsafe_request_blocked": resolve_unsafe_blocked_flag(
                    result=result,
                ),
                "blocked_reason": resolve_blocked_reason(result=result),
                "blocked_terms": resolve_blocked_terms(result=result),
                "document_id": data.get("document_id"),
                "document_title": data.get("document_title"),
                "selected_document_file_name": data.get(
                    "selected_document_file_name"
                ),
                "pending_clarification": data.get("pending_clarification"),
                "clarification_options": data.get("clarification_options", []),
                "clarification_question": data.get("clarification_question"),
                "should_exit": data.get("should_exit", False),
                "planning_source": data.get("planning_source"),
                "planning_errors": data.get("planning_errors", []),
                "planning_warnings": data.get("planning_warnings", []),
                "research_plan": research_plan,
                "research_task_results": research_task_results,
                "research_gaps": research_gaps,
                "research_report": research_report,
                "research_trace": research_trace,
                "retrieval_strategy_errors": data.get(
                    "retrieval_strategy_errors",
                    [],
                ),
            }
        ),
        errors=extract_turn_errors(result),
    )
