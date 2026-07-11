from __future__ import annotations

from src.application.langgraph.common import (
    GraphResult,
    is_safe_failure_message,
    is_usable_reflection_decision,
)
from src.application.langgraph.graphs.document_agent import (
    document_agent_answer_extractor as answer_extractor,
)
from src.application.langgraph.graphs.document_agent.document_agent_context_chunk_enricher import (
    extract_context_chunks,
)
from src.application.langgraph.state import AgentState


def build_result(state: AgentState) -> GraphResult:
    route = state.get("route")
    tool_results = state.get("tool_results", {})
    reflection_decision = state.get("reflection_decision")
    answer = answer_extractor.extract_answer(
        tool_results,
        state.get("response_text"),
        reflection_decision=reflection_decision,
    )
    if (
        is_usable_reflection_decision(reflection_decision)
        and is_safe_failure_message(answer)
    ):
        recovered_answer = answer_extractor.extract_answer(
            tool_results,
            None,
            reflection_decision=reflection_decision,
        )
        if recovered_answer and not is_safe_failure_message(recovered_answer):
            answer = recovered_answer
    answer_intent = answer_extractor.extract_answer_intent(tool_results)
    citations = answer_extractor.extract_citations(tool_results)
    limitation_note = answer_extractor.extract_limitation_note(tool_results)
    sections = answer_extractor.extract_sections(tool_results)
    reference_notes = answer_extractor.extract_reference_notes(tool_results)
    context_chunks = extract_context_chunks(
        tool_results=tool_results,
        citations=citations,
        fallback_document_title=state.get("document_title")
        or state.get("selected_document_title"),
        selected_document_id=state.get("selected_document_id")
        or state.get("document_id"),
    )
    diagnostics = {
        "needs_clarification": state.get("needs_clarification", False),
        "configured_tools": sorted(tool_results.keys()),
        "plan_used": bool(state.get("execution_plan")),
        "plan_success": state.get("plan_success"),
        "planning_source": state.get("planning_source"),
        "unsafe_request_blocked": state.get("unsafe_request_blocked", False),
        "guardrail_decision": state.get("guardrail_decision"),
        "guardrail_trace_id": state.get("guardrail_trace_id"),
        "reflection_enabled": state.get("reflection_enabled", False),
        "retrieval_strategy_enabled": state.get("retrieval_strategy_enabled", False),
        "deep_research_enabled": state.get("deep_research_enabled", False),
        "research_plan_source": state.get("research_plan_source"),
        "strategy_advisor_status": (
            (state.get("strategy_advisor_result") or {}).get("status")
            if isinstance(state.get("strategy_advisor_result"), dict)
            else None
        ),
    }
    data = {
        "document_id": state.get("document_id"),
        "document_title": state.get("document_title"),
        "selected_document_id": state.get("selected_document_id"),
        "selected_document_title": state.get("selected_document_title"),
        "selected_document_file_name": state.get("selected_document_file_name"),
        "pending_clarification": state.get("pending_clarification"),
        "clarification_options": state.get("clarification_options", []),
        "clarification_question": state.get("clarification_question"),
        "should_exit": state.get("should_exit", False),
        "answer": answer,
        "final_response_warning": state.get("final_response_warning"),
        "answer_intent": answer_intent,
        "context_chunks": context_chunks,
        "citations": citations,
        "limitation_note": limitation_note,
        "sections": sections,
        "reference_notes": reference_notes,
        "reflection_result": state.get("reflection_result"),
        "reflection_decision": state.get("reflection_decision"),
        "reflection_score": state.get("reflection_score"),
        "answer_quality": state.get("answer_quality"),
        "evidence_quality": state.get("evidence_quality"),
        "retry_query": state.get("retry_query"),
        "reflection_trace": state.get("reflection_trace", []),
        "initial_context_chunks": state.get("initial_context_chunks", []),
        "retry_context_chunks": state.get("retry_context_chunks", []),
        "merged_context_chunks": state.get("merged_context_chunks", []),
        "merged_chunk_ids": state.get("merged_chunk_ids", []),
        "retrieval_strategy_decision": state.get("retrieval_strategy_decision"),
        "retrieval_plan": state.get("retrieval_plan"),
        "retrieval_execution_result": state.get("retrieval_execution_result"),
        "retrieval_strategy_trace": state.get("retrieval_strategy_trace"),
        "strategy_advisor_result": state.get("strategy_advisor_result"),
        "strategy_advisor_trace": state.get("strategy_advisor_trace"),
        "selected_retrieval_strategies": state.get(
            "selected_retrieval_strategies",
            [],
        ),
        "retrieval_strategy_errors": state.get("retrieval_strategy_errors", []),
        "execution_plan": state.get("execution_plan"),
        "validated_plan": state.get("validated_plan"),
        "plan_steps": state.get("plan_steps", []),
        "plan_results": state.get("plan_results", {}),
        "plan_success": state.get("plan_success"),
        "failed_plan_step": state.get("failed_plan_step"),
        "planning_source": state.get("planning_source"),
        "planning_errors": state.get("planning_errors", []),
        "planning_warnings": state.get("planning_warnings", []),
        "raw_llm_plan": state.get("raw_llm_plan"),
        "research_goal": state.get("research_goal"),
        "research_plan": state.get("research_plan"),
        "research_task_results": state.get("research_task_results", []),
        "research_evidence": state.get("research_evidence", []),
        "research_gaps": state.get("research_gaps", []),
        "research_iterations": state.get("research_iterations", 0),
        "research_synthesis": state.get("research_synthesis"),
        "research_report": state.get("research_report"),
        "research_errors": state.get("research_errors", []),
        "research_trace": state.get("research_trace"),
        "research_plan_source": state.get("research_plan_source"),
        "research_planning_errors": state.get("research_planning_errors", []),
        "research_planning_warnings": state.get(
            "research_planning_warnings",
            [],
        ),
        "raw_llm_research_plan": state.get("raw_llm_research_plan"),
        "unsafe_request_blocked": state.get("unsafe_request_blocked", False),
        "blocked_reason": state.get("blocked_reason"),
        "blocked_terms": state.get("blocked_terms", []),
        "blocked_tools": state.get("blocked_tools", []),
        "guardrail_decision": state.get("guardrail_decision"),
        "guardrail_result": state.get("guardrail_result"),
        "guardrail_user_message": state.get("guardrail_user_message"),
        "guardrail_trace_id": state.get("guardrail_trace_id"),
        "guardrail_trace": state.get("guardrail_trace", []),
        "tool_results": tool_results,
    }
    execution_plan = state.get("execution_plan")
    if isinstance(execution_plan, dict):
        diagnostics["plan_id"] = execution_plan.get("plan_id")
        diagnostics["plan_goal"] = execution_plan.get("goal")
    if state.get("planning_errors"):
        diagnostics["planning_errors"] = state.get("planning_errors", [])
    if state.get("planning_warnings"):
        diagnostics["planning_warnings"] = state.get("planning_warnings", [])
    if state.get("blocked_reason"):
        diagnostics["blocked_reason"] = state.get("blocked_reason")
    if state.get("blocked_terms"):
        diagnostics["blocked_terms"] = state.get("blocked_terms", [])
    if state.get("blocked_tools"):
        diagnostics["blocked_tools"] = state.get("blocked_tools", [])
    if state.get("guardrail_trace"):
        diagnostics["guardrail_trace"] = state.get("guardrail_trace", [])
    if answer_intent is not None:
        diagnostics["answer_intent"] = answer_intent
    if state.get("reflection_decision"):
        diagnostics["reflection_decision"] = state.get("reflection_decision")
        diagnostics["reflection_score"] = state.get("reflection_score")
    if state.get("final_response_warning"):
        diagnostics["final_response_warning"] = state.get("final_response_warning")
    retrieval_strategy_decision = state.get("retrieval_strategy_decision")
    if isinstance(retrieval_strategy_decision, dict):
        diagnostics["retrieval_strategy_primary"] = retrieval_strategy_decision.get(
            "primary_strategy"
        )
        diagnostics["retrieval_strategy_secondaries"] = (
            retrieval_strategy_decision.get("secondary_strategies", [])
        )
    if state.get("retrieval_strategy_errors"):
        diagnostics["retrieval_strategy_errors"] = state.get(
            "retrieval_strategy_errors",
            [],
        )
    if state.get("research_planning_errors"):
        diagnostics["research_planning_errors"] = state.get(
            "research_planning_errors",
            [],
        )
    if state.get("research_planning_warnings"):
        diagnostics["research_planning_warnings"] = state.get(
            "research_planning_warnings",
            [],
        )
    if state.get("research_errors"):
        diagnostics["research_errors"] = state.get("research_errors", [])
    if state.get("needs_clarification") and state.get("error") is None:
        return GraphResult.ok(
            response_text=state.get("response_text"),
            data=data,
            route=route,
            diagnostics=diagnostics,
            trace=state.get("trace", []),
            messages=state.get("history", []),
        )
    if state.get("error") is not None:
        error = state["error"]
        diagnostics["error"] = error.get("diagnostics", {})
        return GraphResult.fail(
            response_text=state.get("response_text"),
            error_code=error.get("error_code"),
            data=data,
            route=route,
            diagnostics=diagnostics,
            trace=state.get("trace", []),
            messages=state.get("history", []),
        )
    return GraphResult.ok(
        response_text=answer or state.get("response_text"),
        data=data,
        route=route,
        diagnostics=diagnostics,
        trace=state.get("trace", []),
        messages=state.get("history", []),
    )
