from dataclasses import dataclass

from src.application.contracts.guardrails.violation_type import ViolationType


@dataclass(slots=True, frozen=True)
class GuardrailViolation:
    violation_type: ViolationType
    message: str
    chunk_id: str | None = None
    field: str | None = None
