from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ReflectionDecisionType(StrEnum):
    ACCEPT = "ACCEPT"
    RETRIEVE_AGAIN = "RETRIEVE_AGAIN"
    CLARIFY = "CLARIFY"
    FAIL = "FAIL"


@dataclass(slots=True)
class ReflectionDecision:
    decision: ReflectionDecisionType
    confidence: float
    reason: str
    retry_query: str | None = None
    clarification_question: str | None = None
    missing_information: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
