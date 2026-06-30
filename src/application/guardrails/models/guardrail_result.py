from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from src.application.guardrails.models.confidence_level import ConfidenceLevel
from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.models.guardrail_violation import GuardrailViolation


def _serialize_guardrail_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {
            str(key): _serialize_guardrail_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple | set | frozenset):
        return [_serialize_guardrail_value(item) for item in value]
    return value


@dataclass(slots=True)
class GuardrailResult:
    decision: GuardrailDecision
    allowed: bool
    reason: str

    severity: GuardrailSeverity | None = None
    user_message: str | None = None
    violations: list[GuardrailViolation] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None

    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    evidence_summary: str | None = None
    approved_chunk_ids: list[str] = field(default_factory=list)
    rejected_chunk_ids: list[str] = field(default_factory=list)
    required_citations: list[str] = field(default_factory=list)
    safe_user_message: str | None = None

    def __post_init__(self) -> None:
        if self.severity is None:
            self.severity = GuardrailSeverity.INFO if self.allowed else GuardrailSeverity.MEDIUM
        if self.user_message is None and self.safe_user_message is not None:
            self.user_message = self.safe_user_message
        if self.safe_user_message is None and self.user_message is not None:
            self.safe_user_message = self.user_message

    def to_dict(self) -> dict[str, Any]:
        return _serialize_guardrail_value(asdict(self))
