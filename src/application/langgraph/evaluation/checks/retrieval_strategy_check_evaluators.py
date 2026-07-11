from __future__ import annotations

from src.application.langgraph.evaluation.agent_eval_result import AgentTurnResult
from src.application.langgraph.evaluation.agent_test_case import AgentExpectedBehavior
from src.application.langgraph.evaluation.checks.safety_check_evaluators import (
    evaluate_document_scope,
)
from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy


def evaluate_retrieval_strategy_selection(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if (
        expected.retrieval_strategy_primary is None
        and not expected.retrieval_strategy_secondary_contains
    ):
        return None
    if final_turn.retrieval_strategy_primary != expected.retrieval_strategy_primary:
        return False
    actual_secondaries = set(final_turn.retrieval_strategy_secondary)
    return all(
        expected_secondary in actual_secondaries
        for expected_secondary in expected.retrieval_strategy_secondary_contains
    )


def evaluate_retrieval_strategy_validity(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if not _strategy_metric_applicable(expected, final_turn=final_turn):
        return None
    if final_turn.retrieval_strategy_primary is None:
        return False
    allowed = {strategy.value for strategy in RetrievalStrategy}
    if final_turn.retrieval_strategy_primary not in allowed:
        return False
    if any(
        secondary not in allowed for secondary in final_turn.retrieval_strategy_secondary
    ):
        return False
    if len(final_turn.retrieval_strategy_secondary) != len(
        set(final_turn.retrieval_strategy_secondary)
    ):
        return False
    return True


def evaluate_multi_strategy_success(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if expected.retrieval_strategy_primary != RetrievalStrategy.MULTI_STRATEGY.value:
        return None
    return evaluate_retrieval_strategy_selection(expected, final_turn=final_turn)


def evaluate_strategy_document_scope(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if not _strategy_metric_applicable(expected, final_turn=final_turn):
        return None
    return evaluate_document_scope(expected, final_turn=final_turn)


def evaluate_strategy_trace_coverage(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool | None:
    if expected.retrieval_strategy_trace_required is not None:
        return (
            final_turn.retrieval_strategy_trace_present
            == expected.retrieval_strategy_trace_required
        )
    if not _strategy_metric_applicable(expected, final_turn=final_turn):
        return None
    return final_turn.retrieval_strategy_trace_present


def evaluate_strategy_fallback_rate(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> float | None:
    if not _strategy_metric_applicable(expected, final_turn=final_turn):
        return None
    return 1.0 if final_turn.retrieval_strategy_fallback_used else 0.0


def _strategy_metric_applicable(
    expected: AgentExpectedBehavior,
    *,
    final_turn: AgentTurnResult,
) -> bool:
    return bool(
        expected.retrieval_strategy_primary is not None
        or expected.retrieval_strategy_trace_required is not None
        or final_turn.retrieval_strategy_enabled
        or final_turn.retrieval_strategy_primary is not None
    )
