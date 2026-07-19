from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class SufficiencyVerdictType(StrEnum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT_RETRY = "INSUFFICIENT_RETRY"
    INSUFFICIENT_CLARIFY = "INSUFFICIENT_CLARIFY"


@dataclass(slots=True)
class SufficiencyVerdict:
    """Output of an `EvidenceSufficiencyStrategy` -- the generic, intent-keyed
    replacement for the hardcoded per-domain context/relevance detectors."""

    verdict: SufficiencyVerdictType
    reason: str
    missing_information: list[str] = field(default_factory=list)

    @property
    def is_sufficient(self) -> bool:
        return self.verdict == SufficiencyVerdictType.SUFFICIENT
