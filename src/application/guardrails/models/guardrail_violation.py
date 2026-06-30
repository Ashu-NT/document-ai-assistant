from __future__ import annotations

from dataclasses import dataclass, field

from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.models.violation_type import ViolationType


@dataclass(slots=True, frozen=True)
class GuardrailViolation:
    violation_type: ViolationType | str
    description: str = ""
    matched_terms: list[str] = field(default_factory=list)
    policy_name: str | None = None
    severity: GuardrailSeverity | None = None
    chunk_id: str | None = None
    field: str | None = None
    message: str | None = None

    def __post_init__(self) -> None:
        description = self.description or self.message or ""
        message = self.message or self.description or ""
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "message", message)
