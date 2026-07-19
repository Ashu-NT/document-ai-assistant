from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType


class SeedEvidenceGuardrail:

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.retrieved_chunks:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason=f"Retrieval returned {len(context.retrieved_chunks)} candidate chunk(s).",
            )
        return GuardrailResult(
            decision=GuardrailDecision.NO_EVIDENCE,
            allowed=False,
            reason="No retrieval evidence found for this query.",
            confidence=ConfidenceLevel.HIGH,
            violations=[
                GuardrailViolation(
                    violation_type=ViolationType.NO_EVIDENCE,
                    message="Retrieval returned zero chunks.",
                )
            ],
            safe_user_message=(
                "No relevant information was found in the knowledge base for your query."
            ),
        )
