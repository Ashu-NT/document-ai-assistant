from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.retrieval_guardrail_policy import (
    RetrievalGuardrailPolicy,
)


class IdentifierEvidenceGuardrail:
    def __init__(self, policy: RetrievalGuardrailPolicy | None = None) -> None:
        self._policy = policy or RetrievalGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if not self._policy.identifier_evidence_required:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Identifier evidence check is disabled by policy.",
            )

        if not context.detected_identifiers:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No identifiers detected in query.",
            )

        missing = [
            identifier
            for identifier in context.detected_identifiers
            if not self._any_chunk_mentions(identifier, context)
        ]

        if missing:
            return GuardrailResult(
                decision=GuardrailDecision.INSUFFICIENT_EVIDENCE,
                allowed=False,
                reason=(
                    f"No evidence found for identifier(s): {', '.join(missing)}."
                ),
                confidence=ConfidenceLevel.HIGH,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.IDENTIFIER_NOT_FOUND,
                        message=f"Identifier '{identifier}' not found in any retrieved chunk.",
                    )
                    for identifier in missing
                ],
                safe_user_message=(
                    f"The requested identifier(s) ({', '.join(missing)}) "
                    "were not found in the available documents."
                ),
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason="All detected identifiers have supporting evidence.",
        )

    @staticmethod
    def _any_chunk_mentions(identifier: str, context: GuardrailContext) -> bool:
        normalized = identifier.strip().lower()
        return any(
            normalized in chunk.content.lower()
            for chunk in context.retrieved_chunks
        )
