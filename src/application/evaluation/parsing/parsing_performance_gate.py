from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.application.evaluation.parsing.parsing_performance_thresholds import (
    ParsingPerformanceThresholds,
)


@dataclass(frozen=True, slots=True)
class ParsingPerformanceViolation:
    stage: str
    actual_seconds: float | None
    threshold_seconds: float
    message: str


@dataclass
class ParsingPerformanceGateResult:
    passed: bool
    violations: list[ParsingPerformanceViolation] = field(default_factory=list)
    checked_stages: dict[str, float | None] = field(default_factory=dict)

    def summary(self) -> str:
        if self.passed:
            return f"PASS — all {len(self.checked_stages)} stage(s) within thresholds"
        lines = [f"FAIL — {len(self.violations)} threshold violation(s):"]
        for violation in self.violations:
            actual_text = (
                f"{violation.actual_seconds:.3f}s"
                if violation.actual_seconds is not None
                else "n/a"
            )
            lines.append(
                f"  {violation.stage}: {actual_text} > "
                f"{violation.threshold_seconds:.3f}s (threshold)"
            )
        return "\n".join(lines)


class ParsingPerformanceGate:
    """Checks measured parsing stage durations against configured ceilings.

    Mirrors `RetrievalQualityGate`'s shape: thresholds come from YAML (no
    hardcoded Python fallback — a missing/malformed thresholds file is a
    configuration error, not a signal to skip checks), and `check()` takes
    a plain `stage_durations` mapping so it can be run against a live
    `ParsingWorkflowResult.stage_durations` or a persisted report.
    """

    def __init__(
        self,
        thresholds: ParsingPerformanceThresholds | None = None,
        thresholds_path: Path | str | None = None,
    ) -> None:
        self._thresholds = thresholds or ParsingPerformanceThresholds.from_yaml(
            thresholds_path
        )

    def check(self, stage_durations: dict[str, float]) -> ParsingPerformanceGateResult:
        t = self._thresholds
        violations: list[ParsingPerformanceViolation] = []
        checked: dict[str, float | None] = {}

        # (display_name, stage_durations key, threshold)
        checks = [
            ("docling_conversion", "docling_conversion", t.docling_conversion_max_seconds),
            (
                "canonical_normalization",
                "canonical_normalization",
                t.canonical_normalization_max_seconds,
            ),
            ("graph_build", "graph_build", t.graph_build_max_seconds),
            ("total", "total", t.total_max_seconds),
        ]
        for stage, duration_key, threshold in checks:
            if threshold is None:
                continue
            actual = stage_durations.get(duration_key)
            checked[stage] = actual
            if actual is None or actual > threshold:
                violations.append(
                    ParsingPerformanceViolation(
                        stage=stage,
                        actual_seconds=actual,
                        threshold_seconds=threshold,
                        message=f"{stage} took {actual}s, exceeding {threshold}s",
                    )
                )

        return ParsingPerformanceGateResult(
            passed=len(violations) == 0,
            violations=violations,
            checked_stages=checked,
        )
