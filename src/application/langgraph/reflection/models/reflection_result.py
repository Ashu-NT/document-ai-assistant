from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.reflection.models.reflection_decision import (
    ReflectionDecision,
)


@dataclass(slots=True)
class ReflectionResult:
    decision: ReflectionDecision
    answer_quality_score: float
    evidence_quality_score: float
    grounding_score: float
    document_scope_score: float
    overall_score: float
    accepted: bool
    requires_retry: bool
    requires_clarification: bool
    failed: bool
    diagnostics: dict[str, Any] = field(default_factory=dict)
