from __future__ import annotations

from dataclasses import dataclass, field

from src.application.validation.document_quality.quality_check_result import (
    QualityCheckResult,
    QualityCheckSeverity,
)


@dataclass
class DocumentQualityResult:
    document_id: str
    checks: list[QualityCheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(
            not r.passed and r.severity == QualityCheckSeverity.ERROR
            for r in self.checks
        )

    @property
    def warning_count(self) -> int:
        return sum(
            1
            for r in self.checks
            if not r.passed and r.severity == QualityCheckSeverity.WARNING
        )

    @property
    def error_count(self) -> int:
        return sum(
            1
            for r in self.checks
            if not r.passed and r.severity == QualityCheckSeverity.ERROR
        )

    def failures(self) -> list[QualityCheckResult]:
        return [r for r in self.checks if not r.passed]

    def summary(self) -> str:
        total = len(self.checks)
        return (
            f"{'PASS' if self.passed else 'FAIL'} "
            f"{total - len(self.failures())}/{total} checks passed "
            f"({self.error_count} errors, {self.warning_count} warnings)"
        )
