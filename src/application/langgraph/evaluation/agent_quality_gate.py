from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.application.langgraph.evaluation.models.agent_eval_metric_registry import (
    AGENT_EVAL_THRESHOLD_METRIC_NAMES,
)
from src.application.langgraph.evaluation.models.agent_eval_result import AgentEvalReport
from src.application.langgraph.evaluation.models.agent_eval_thresholds import (
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
            (metric_name, getattr(summary, metric_name), getattr(thresholds, metric_name))
            for metric_name in AGENT_EVAL_THRESHOLD_METRIC_NAMES
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
