from dataclasses import dataclass, field

from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation


@dataclass(slots=True)
class GuardrailResult:
    decision: GuardrailDecision
    allowed: bool
    reason: str

    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    violations: list[GuardrailViolation] = field(default_factory=list)

    evidence_summary: str | None = None
    approved_chunk_ids: list[str] = field(default_factory=list)
    rejected_chunk_ids: list[str] = field(default_factory=list)
    required_citations: list[str] = field(default_factory=list)
    safe_user_message: str | None = None
