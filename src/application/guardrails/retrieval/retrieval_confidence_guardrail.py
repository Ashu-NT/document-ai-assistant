from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.retrieval_guardrail_policy import (
    RetrievalGuardrailPolicy,
)


class RetrievalConfidenceGuardrail:
    def __init__(self, policy: RetrievalGuardrailPolicy | None = None) -> None:
        self._policy = policy or RetrievalGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if not context.retrieved_chunks:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No chunks to evaluate confidence for.",
            )

        best_score = max(chunk.score for chunk in context.retrieved_chunks)
        threshold = self._policy.min_retrieval_score

        if best_score < threshold:
            return GuardrailResult(
                decision=GuardrailDecision.LOW_CONFIDENCE,
                allowed=False,
                reason=(
                    f"Best retrieval score {best_score:.3f} is below "
                    f"the minimum threshold of {threshold:.3f}."
                ),
                confidence=ConfidenceLevel.LOW,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.LOW_CONFIDENCE_SCORE,
                        message=(
                            f"Highest retrieval score {best_score:.3f} "
                            f"does not meet the required minimum of {threshold:.3f}."
                        ),
                    )
                ],
                evidence_summary=f"Best score: {best_score:.3f} (threshold: {threshold:.3f}).",
                safe_user_message=(
                    "The retrieved information may not be sufficiently relevant "
                    "to answer your question reliably."
                ),
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason=f"Best retrieval score {best_score:.3f} meets the threshold.",
            evidence_summary=f"Best score: {best_score:.3f}.",
        )
