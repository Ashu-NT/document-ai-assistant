from __future__ import annotations

from dataclasses import dataclass, field

from src.application.guardrails.models.guardrail_severity import GuardrailSeverity


@dataclass(slots=True, frozen=True)
class DetectorMatch:
    matched: bool
    reason: str | None = None
    matched_terms: list[str] = field(default_factory=list)
    severity: GuardrailSeverity = GuardrailSeverity.MEDIUM
