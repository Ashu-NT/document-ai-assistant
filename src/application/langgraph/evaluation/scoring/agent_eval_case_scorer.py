from __future__ import annotations

from typing import Any, Sequence

from src.application.langgraph.evaluation.models.agent_eval_result import AgentTurnResult
from src.application.langgraph.evaluation.models.agent_test_case import AgentExpectedBehavior
from src.application.langgraph.evaluation.checks.policy_check_evaluators import (
    evaluate_answer_expectations,
    evaluate_plan_policy,
    evaluate_tool_policy,
)
from src.application.langgraph.evaluation.checks.research_check_evaluators import (
    evaluate_deep_research_route,
    evaluate_research_citation_coverage,
    evaluate_research_document_scope,
    evaluate_research_gap_detection,
    evaluate_research_plan_validity,
    evaluate_research_report_completeness,
    evaluate_research_task_success_rate,
)
from src.application.langgraph.evaluation.checks.retrieval_strategy_check_evaluators import (
    evaluate_multi_strategy_success,
    evaluate_retrieval_strategy_selection,
    evaluate_retrieval_strategy_validity,
    evaluate_strategy_document_scope,
    evaluate_strategy_fallback_rate,
    evaluate_strategy_trace_coverage,
)
from src.application.langgraph.evaluation.checks.routing_check_evaluators import (
    evaluate_document_selection,
    turn_requires_clarification,
)
from src.application.langgraph.evaluation.checks.safety_check_evaluators import (
    evaluate_destructive_tool_block,
    evaluate_document_scope,
    evaluate_false_negative_guardrail,
    evaluate_false_positive_guardrail,
    evaluate_grounding_failure_catch,
    evaluate_guardrail_block,
    evaluate_out_of_scope_redirect,
    evaluate_prompt_injection_block,
    evaluate_unsafe_block,
)
from src.application.langgraph.evaluation.scoring.eval_metric_recorder import (
    record_check,
)
from src.application.langgraph.evaluation.scoring.eval_value_helpers import (
    evaluate_optional_bool,
    unique_preserving_order,
)


def evaluate_case(
    expected: AgentExpectedBehavior,
    *,
    turn_results: Sequence[AgentTurnResult],
) -> tuple[list[str], dict[str, float], dict[str, Any]]:
    final_turn = turn_results[-1]
    all_tool_names = unique_preserving_order(
        tool_name
        for turn_result in turn_results
        for tool_name in turn_result.tool_names
    )
    all_plan_tool_names = unique_preserving_order(
        tool_name
        for turn_result in turn_results
        for tool_name in turn_result.plan_tool_names
    )
    metrics: dict[str, float] = {}
    failed_checks: list[str] = []

    route_pass = evaluate_optional_bool(
        expected.final_route is not None,
        final_turn.route == expected.final_route,
    )
    record_check(
        "route_accuracy",
        route_pass,
        metrics,
        failed_checks,
    )

    deep_research_route_pass = evaluate_deep_research_route(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "deep_research_route_accuracy",
        deep_research_route_pass,
        metrics,
        failed_checks,
    )

    document_selection_pass = evaluate_document_selection(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "document_selection_accuracy",
        document_selection_pass,
        metrics,
        failed_checks,
    )

    clarification_pass = evaluate_optional_bool(
        expected.should_clarify is not None,
        turn_requires_clarification(final_turn) == expected.should_clarify,
    )
    record_check(
        "clarification_accuracy",
        clarification_pass,
        metrics,
        failed_checks,
    )

    success_pass = evaluate_optional_bool(
        expected.success is not None,
        final_turn.success == expected.success,
    )
    if success_pass is False:
        failed_checks.append("success")

    should_exit_pass = evaluate_optional_bool(
        expected.should_exit is not None,
        bool(final_turn.diagnostics.get("should_exit")) == expected.should_exit,
    )
    if should_exit_pass is False:
        failed_checks.append("should_exit")

    tool_policy_pass = evaluate_tool_policy(
        expected,
        tool_names=all_tool_names,
    )
    record_check(
        "tool_policy_compliance_rate",
        tool_policy_pass,
        metrics,
        failed_checks,
    )

    plan_validity_pass = evaluate_plan_policy(
        expected,
        plan_tool_names=all_plan_tool_names,
    )
    record_check(
        "plan_validity_rate",
        plan_validity_pass,
        metrics,
        failed_checks,
    )

    unsafe_block_pass = evaluate_unsafe_block(
        expected,
        final_turn=final_turn,
        tool_names=all_tool_names,
    )
    record_check(
        "unsafe_block_rate",
        unsafe_block_pass,
        metrics,
        failed_checks,
    )

    guardrail_block_pass = evaluate_guardrail_block(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "guardrail_block_rate",
        guardrail_block_pass,
        metrics,
        failed_checks,
    )

    out_of_scope_redirect_pass = evaluate_out_of_scope_redirect(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "out_of_scope_redirect_rate",
        out_of_scope_redirect_pass,
        metrics,
        failed_checks,
    )

    prompt_injection_block_pass = evaluate_prompt_injection_block(final_turn)
    record_check(
        "prompt_injection_block_rate",
        prompt_injection_block_pass,
        metrics,
        failed_checks,
    )

    destructive_tool_block_pass = evaluate_destructive_tool_block(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "destructive_tool_block_rate",
        destructive_tool_block_pass,
        metrics,
        failed_checks,
    )

    grounding_failure_catch_pass = evaluate_grounding_failure_catch(final_turn)
    record_check(
        "grounding_failure_catch_rate",
        grounding_failure_catch_pass,
        metrics,
        failed_checks,
    )

    document_scope_pass = evaluate_document_scope(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "document_scope_safety_rate",
        document_scope_pass,
        metrics,
        failed_checks,
    )

    answer_expectation_pass = evaluate_answer_expectations(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "answer_expectation_rate",
        answer_expectation_pass,
        metrics,
        failed_checks,
    )

    false_positive_guardrail = evaluate_false_positive_guardrail(
        expected,
        final_turn=final_turn,
    )
    if false_positive_guardrail is not None:
        metrics["false_positive_guardrail_rate"] = (
            1.0 if false_positive_guardrail else 0.0
        )
        if false_positive_guardrail:
            failed_checks.append("false_positive_guardrail_rate")

    false_negative_guardrail = evaluate_false_negative_guardrail(
        expected,
        final_turn=final_turn,
    )
    if false_negative_guardrail is not None:
        metrics["false_negative_guardrail_rate"] = (
            1.0 if false_negative_guardrail else 0.0
        )
        if false_negative_guardrail:
            failed_checks.append("false_negative_guardrail_rate")

    retrieval_strategy_selection_pass = evaluate_retrieval_strategy_selection(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "retrieval_strategy_selection_rate",
        retrieval_strategy_selection_pass,
        metrics,
        failed_checks,
    )

    retrieval_strategy_validity_pass = evaluate_retrieval_strategy_validity(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "retrieval_strategy_validity_rate",
        retrieval_strategy_validity_pass,
        metrics,
        failed_checks,
    )

    multi_strategy_success_pass = evaluate_multi_strategy_success(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "multi_strategy_success_rate",
        multi_strategy_success_pass,
        metrics,
        failed_checks,
    )

    strategy_document_scope_pass = evaluate_strategy_document_scope(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "strategy_document_scope_safety_rate",
        strategy_document_scope_pass,
        metrics,
        failed_checks,
    )

    strategy_trace_coverage_pass = evaluate_strategy_trace_coverage(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "strategy_trace_coverage_rate",
        strategy_trace_coverage_pass,
        metrics,
        failed_checks,
    )

    research_plan_validity_pass = evaluate_research_plan_validity(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "research_plan_validity_rate",
        research_plan_validity_pass,
        metrics,
        failed_checks,
    )

    research_task_success_rate = evaluate_research_task_success_rate(
        expected,
        final_turn=final_turn,
        failed_checks=failed_checks,
    )
    if research_task_success_rate is not None:
        metrics["research_task_success_rate"] = research_task_success_rate

    research_gap_detection_pass = evaluate_research_gap_detection(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "research_gap_detection_rate",
        research_gap_detection_pass,
        metrics,
        failed_checks,
    )

    research_document_scope_pass = evaluate_research_document_scope(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "research_document_scope_safety_rate",
        research_document_scope_pass,
        metrics,
        failed_checks,
    )

    research_report_completeness_pass = evaluate_research_report_completeness(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "research_report_completeness_rate",
        research_report_completeness_pass,
        metrics,
        failed_checks,
    )

    research_citation_coverage_pass = evaluate_research_citation_coverage(
        expected,
        final_turn=final_turn,
    )
    record_check(
        "research_citation_coverage_rate",
        research_citation_coverage_pass,
        metrics,
        failed_checks,
    )

    strategy_fallback_rate = evaluate_strategy_fallback_rate(
        expected,
        final_turn=final_turn,
    )
    if strategy_fallback_rate is not None:
        metrics["strategy_fallback_rate"] = strategy_fallback_rate

    return failed_checks, metrics, {
        "all_tool_names": all_tool_names,
        "all_plan_tool_names": all_plan_tool_names,
        "final_route": final_turn.route,
        "final_success": final_turn.success,
        "final_selected_document_id": final_turn.selected_document_id,
        "final_selected_document_title": final_turn.selected_document_title,
        "final_context_document_ids": final_turn.context_document_ids,
        "final_retrieval_strategy_primary": final_turn.retrieval_strategy_primary,
        "final_retrieval_strategy_secondary": (
            final_turn.retrieval_strategy_secondary
        ),
    }
