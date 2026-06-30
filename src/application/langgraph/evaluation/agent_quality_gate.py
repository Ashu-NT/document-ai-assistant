from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.application.langgraph.evaluation.agent_eval_result import AgentEvalReport
from src.application.langgraph.evaluation.agent_eval_thresholds import (
    AgentEvalThresholds,
)


@dataclass(frozen=True, slots=True)
class AgentThresholdViolation:
    metric: str
    actual: float | None
    threshold: float
    message: str


@dataclass(slots=True)
class AgentQualityGateResult:
    passed: bool
    violations: list[AgentThresholdViolation] = field(default_factory=list)
    checked_metrics: dict[str, float | None] = field(default_factory=dict)

    def summary(self) -> str:
        if self.passed:
            return f"PASS - all {len(self.checked_metrics)} metrics above thresholds"
        lines = [f"FAIL - {len(self.violations)} threshold violation(s):"]
        for violation in self.violations:
            actual_text = (
                f"{violation.actual:.4f}"
                if violation.actual is not None
                else "n/a"
            )
            lines.append(
                (
                    f"  {violation.metric}: {actual_text} < "
                    f"{violation.threshold:.4f} (threshold)"
                )
            )
        return "\n".join(lines)


class AgentQualityGate:
    def __init__(
        self,
        thresholds: AgentEvalThresholds | None = None,
        thresholds_path: Path | str | None = None,
    ) -> None:
        self._thresholds = (
            thresholds
            if thresholds is not None
            else AgentEvalThresholds.from_yaml(thresholds_path)
        )

    def check(self, report: AgentEvalReport) -> AgentQualityGateResult:
        if report.summary is None:
            return AgentQualityGateResult(
                passed=False,
                violations=[
                    AgentThresholdViolation(
                        metric="summary",
                        actual=None,
                        threshold=0.0,
                        message="Agent evaluation report did not include a summary.",
                    )
                ],
                checked_metrics={},
            )

        summary = report.summary
        thresholds = self._thresholds
        checks = [
            ("route_accuracy", summary.route_accuracy, thresholds.route_accuracy),
            (
                "deep_research_route_accuracy",
                summary.deep_research_route_accuracy,
                thresholds.deep_research_route_accuracy,
            ),
            (
                "document_selection_accuracy",
                summary.document_selection_accuracy,
                thresholds.document_selection_accuracy,
            ),
            (
                "clarification_accuracy",
                summary.clarification_accuracy,
                thresholds.clarification_accuracy,
            ),
            (
                "unsafe_block_rate",
                summary.unsafe_block_rate,
                thresholds.unsafe_block_rate,
            ),
            (
                "plan_validity_rate",
                summary.plan_validity_rate,
                thresholds.plan_validity_rate,
            ),
            (
                "document_scope_safety_rate",
                summary.document_scope_safety_rate,
                thresholds.document_scope_safety_rate,
            ),
            (
                "tool_policy_compliance_rate",
                summary.tool_policy_compliance_rate,
                thresholds.tool_policy_compliance_rate,
            ),
            (
                "answer_expectation_rate",
                summary.answer_expectation_rate,
                thresholds.answer_expectation_rate,
            ),
            (
                "retrieval_strategy_selection_rate",
                summary.retrieval_strategy_selection_rate,
                thresholds.retrieval_strategy_selection_rate,
            ),
            (
                "retrieval_strategy_validity_rate",
                summary.retrieval_strategy_validity_rate,
                thresholds.retrieval_strategy_validity_rate,
            ),
            (
                "strategy_fallback_rate",
                summary.strategy_fallback_rate,
                thresholds.strategy_fallback_rate,
            ),
            (
                "multi_strategy_success_rate",
                summary.multi_strategy_success_rate,
                thresholds.multi_strategy_success_rate,
            ),
            (
                "strategy_document_scope_safety_rate",
                summary.strategy_document_scope_safety_rate,
                thresholds.strategy_document_scope_safety_rate,
            ),
            (
                "strategy_trace_coverage_rate",
                summary.strategy_trace_coverage_rate,
                thresholds.strategy_trace_coverage_rate,
            ),
            (
                "research_plan_validity_rate",
                summary.research_plan_validity_rate,
                thresholds.research_plan_validity_rate,
            ),
            (
                "research_task_success_rate",
                summary.research_task_success_rate,
                thresholds.research_task_success_rate,
            ),
            (
                "research_gap_detection_rate",
                summary.research_gap_detection_rate,
                thresholds.research_gap_detection_rate,
            ),
            (
                "research_document_scope_safety_rate",
                summary.research_document_scope_safety_rate,
                thresholds.research_document_scope_safety_rate,
            ),
            (
                "research_report_completeness_rate",
                summary.research_report_completeness_rate,
                thresholds.research_report_completeness_rate,
            ),
            (
                "research_citation_coverage_rate",
                summary.research_citation_coverage_rate,
                thresholds.research_citation_coverage_rate,
            ),
        ]

        checked_metrics: dict[str, float | None] = {}
        violations: list[AgentThresholdViolation] = []
        for metric, actual, threshold in checks:
            if threshold is None:
                continue
            if not _metric_is_applicable(report, metric):
                continue
            checked_metrics[metric] = actual
            if actual < threshold:
                violations.append(
                    AgentThresholdViolation(
                        metric=metric,
                        actual=actual,
                        threshold=threshold,
                        message=f"{metric}={actual} is below threshold {threshold}",
                    )
                )

        return AgentQualityGateResult(
            passed=len(violations) == 0,
            violations=violations,
            checked_metrics=checked_metrics,
        )


def _metric_is_applicable(report: AgentEvalReport, metric_name: str) -> bool:
    return any(metric_name in case_result.metrics for case_result in report.case_results)
