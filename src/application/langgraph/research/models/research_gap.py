from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class ResearchGapSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(slots=True)
class ResearchGap:
    gap_id: str
    description: str
    severity: ResearchGapSeverity
    related_task_id: str | None
    suggested_followup_query: str | None
    suggested_strategy: str | None
    can_retry: bool
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
