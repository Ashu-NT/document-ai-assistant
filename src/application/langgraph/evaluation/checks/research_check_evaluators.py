from __future__ import annotations

from src.application.langgraph.evaluation.models.agent_eval_result import AgentTurnResult
from src.application.langgraph.evaluation.models.agent_test_case import AgentExpectedBehavior
from src.application.langgraph.routing import RouteType


def evaluate_deep_research_route(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if not _research_metric_applicable(expected, final_turn=final_turn):
        return None
    return final_turn.route == RouteType.DEEP_RESEARCH.value


def evaluate_research_plan_validity(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if not _research_metric_applicable(expected, final_turn=final_turn):
        return None
    if expected.research_plan_required is False:
        return not final_turn.research_plan_present
    return (
        final_turn.research_plan_present
        and final_turn.research_plan_task_count > 0
        and not final_turn.errors
    )


def evaluate_research_task_success_rate(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
    failed_checks: list[str],
) -> float | None:
    if not _research_metric_applicable(expected, final_turn=final_turn):
        return None
    if final_turn.research_task_count <= 0:
        rate = 0.0
    else:
        rate = final_turn.research_task_success_count / final_turn.research_task_count
    minimum = expected.research_task_success_min_rate
    if minimum is not None and rate < minimum:
        failed_checks.append("research_task_success_rate")
    return rate


def evaluate_research_gap_detection(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if expected.research_gap_detection_required is None:
        return None
    return bool(final_turn.research_gap_count > 0) == expected.research_gap_detection_required


def evaluate_research_document_scope(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if not _research_metric_applicable(expected, final_turn=final_turn):
        return None
    expected_scope_id = (
        expected.context_document_id
        or expected.selected_document_id
        or final_turn.selected_document_id
    )
    if expected_scope_id is None:
        return None
    if not final_turn.context_document_ids:
        return False
    return all(
        document_id == expected_scope_id
        for document_id in final_turn.context_document_ids
    )


def evaluate_research_report_completeness(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if not _research_metric_applicable(expected, final_turn=final_turn):
        return None
    if expected.research_report_required is False:
        return not final_turn.research_report_present
    return (
        final_turn.research_report_present
        and final_turn.research_report_section_count > 0
        and bool(final_turn.response_text)
    )


def evaluate_research_citation_coverage(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if (
        expected.research_citation_required is None
        and not _research_metric_applicable(expected, final_turn=final_turn)
    ):
        return None
    has_citations = final_turn.research_citation_count > 0
    if expected.research_citation_required is not None:
        return has_citations == expected.research_citation_required
    return has_citations


def _research_metric_applicable(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool:
    return bool(
        expected.final_route == RouteType.DEEP_RESEARCH.value
        or expected.research_plan_required is not None
        or expected.research_report_required is not None
        or expected.research_gap_detection_required is not None
        or expected.research_citation_required is not None
        or expected.research_task_success_min_rate is not None
        or final_turn.route == RouteType.DEEP_RESEARCH.value
        or final_turn.research_plan_present
        or final_turn.research_report_present
        or final_turn.research_task_count > 0
    )
