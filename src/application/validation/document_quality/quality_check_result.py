from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class QualityCheckSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class QualityCheckResult:
    check_name: str
    passed: bool
    severity: QualityCheckSeverity
    message: str
    details: dict[str, object] = field(default_factory=dict)

    @classmethod
    def ok(cls, check_name: str) -> QualityCheckResult:
        return cls(
            check_name=check_name,
            passed=True,
            severity=QualityCheckSeverity.WARNING,
            message="ok",
        )

    @classmethod
    def warn(
        cls,
        check_name: str,
        message: str,
        details: dict[str, object] | None = None,
    ) -> QualityCheckResult:
        return cls(
            check_name=check_name,
            passed=False,
            severity=QualityCheckSeverity.WARNING,
            message=message,
            details=details or {},
        )

    @classmethod
    def error(
        cls,
        check_name: str,
        message: str,
        details: dict[str, object] | None = None,
    ) -> QualityCheckResult:
        return cls(
            check_name=check_name,
            passed=False,
            severity=QualityCheckSeverity.ERROR,
            message=message,
            details=details or {},
        )
