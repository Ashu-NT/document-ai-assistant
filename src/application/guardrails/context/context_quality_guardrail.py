from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.retrieval_guardrail_policy import (
    RetrievalGuardrailPolicy,
)


class ContextQualityGuardrail:
    def __init__(self, policy: RetrievalGuardrailPolicy | None = None) -> None:
        self._policy = policy or RetrievalGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        approved = context.approved_chunks or context.retrieved_chunks

        if not approved:
            return GuardrailResult(
                decision=GuardrailDecision.INSUFFICIENT_EVIDENCE,
                allowed=False,
                reason="No approved chunks remain after context filtering.",
                confidence=ConfidenceLevel.HIGH,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.NO_EVIDENCE,
                        message="All retrieved chunks were filtered out; no usable context remains.",
                    )
                ],
                safe_user_message=(
                    "The retrieved information did not meet quality requirements."
                ),
            )

        min_chunks = max(context.min_evidence_chunks, self._policy.min_evidence_chunks)
        if len(approved) < min_chunks:
            return GuardrailResult(
                decision=GuardrailDecision.INSUFFICIENT_EVIDENCE,
                allowed=False,
                reason=(
                    f"Only {len(approved)} quality chunk(s) remain, "
                    f"but {min_chunks} are required."
                ),
                confidence=ConfidenceLevel.MEDIUM,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.WEAK_EVIDENCE,
                        message=f"{len(approved)} chunk(s) available after filtering; minimum is {min_chunks}.",
                    )
                ],
                safe_user_message=(
                    "Insufficient high-quality evidence was found to answer the question reliably."
                ),
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason=f"{len(approved)} quality chunk(s) available for context.",
            evidence_summary=f"{len(approved)} approved chunk(s).",
        )
