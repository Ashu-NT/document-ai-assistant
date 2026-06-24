from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.application.evaluation.retrieval.retrieval_quality_thresholds import (
    RetrievalQualityThresholds,
)


@dataclass(frozen=True, slots=True)
class ThresholdViolation:
    metric: str
    actual: float | None
    threshold: float
    message: str


@dataclass
class RetrievalQualityGateResult:
    passed: bool
    violations: list[ThresholdViolation] = field(default_factory=list)
    checked_metrics: dict[str, float | None] = field(default_factory=dict)

    def summary(self) -> str:
        if self.passed:
            return f"PASS — all {len(self.checked_metrics)} metrics above thresholds"
        lines = [f"FAIL — {len(self.violations)} threshold violation(s):"]
        for v in self.violations:
            actual_str = f"{v.actual:.4f}" if v.actual is not None else "n/a"
            lines.append(f"  {v.metric}: {actual_str} < {v.threshold:.4f} (threshold)")
        return "\n".join(lines)


class RetrievalQualityGate:
    def __init__(
        self,
        thresholds: RetrievalQualityThresholds | None = None,
        thresholds_path: Path | str | None = None,
    ) -> None:
        if thresholds is not None:
            self._thresholds = thresholds
        else:
            self._thresholds = RetrievalQualityThresholds.from_yaml(thresholds_path)

    def check(self, report: dict[str, Any]) -> RetrievalQualityGateResult:
        t = self._thresholds
        violations: list[ThresholdViolation] = []
        checked: dict[str, float | None] = {}

        # Metrics live under "summary" in the benchmark report; fall back to root
        # for callers that pass a pre-extracted summary dict.
        summary = report.get("summary", report) if isinstance(report.get("summary"), dict) else report

        # (display_name, report_key, threshold)
        checks = [
            ("hit_rate", "hit_rate", t.hit_rate),
            ("mrr", "mean_reciprocal_rank", t.mrr),
            ("recall_at_5", "recall_at_5", t.recall_at_5),
            ("context_hit_rate", "context_hit_rate", t.context_hit_rate),
            ("identifier_top_1_accuracy", "identifier_top_1_accuracy", t.identifier_top_1_accuracy),
        ]
        for metric, report_key, threshold in checks:
            if threshold is None:
                continue
            raw = summary.get(report_key)
            actual = float(raw) if raw is not None else None
            checked[metric] = actual
            if actual is None or actual < threshold:
                violations.append(
                    ThresholdViolation(
                        metric=metric,
                        actual=actual,
                        threshold=threshold,
                        message=f"{metric}={actual} is below threshold {threshold}",
                    )
                )

        return RetrievalQualityGateResult(
            passed=len(violations) == 0,
            violations=violations,
            checked_metrics=checked,
        )
