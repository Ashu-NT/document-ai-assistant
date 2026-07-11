from __future__ import annotations

from typing import Sequence

from src.application.langgraph.evaluation.agent_eval_metric_registry import (
    AGENT_EVAL_METRIC_NAMES,
)
from src.application.langgraph.evaluation.agent_eval_result import (
    AgentCaseResult,
    AgentEvalSummary,
)


def build_agent_eval_summary(
    case_results: Sequence[AgentCaseResult],
) -> AgentEvalSummary:
    metric_averages = {
        metric_name: _average_metric(case_results, metric_name)
        for metric_name in AGENT_EVAL_METRIC_NAMES
    }
    return AgentEvalSummary(
        case_count=len(case_results),
        passed_count=sum(1 for result in case_results if result.passed),
        failed_count=sum(1 for result in case_results if not result.passed),
        **metric_averages,
    )


def _average_metric(
    case_results: Sequence[AgentCaseResult],
    metric_name: str,
) -> float:
    values = [
        case_result.metrics[metric_name]
        for case_result in case_results
        if metric_name in case_result.metrics
    ]
    if not values:
        return 0.0
    return sum(values) / len(values)
