from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.retrieval_guardrail_policy import (
    RetrievalGuardrailPolicy,
)


class RetrievalEvidenceGuardrail:
    def __init__(self, policy: RetrievalGuardrailPolicy | None = None) -> None:
        self._policy = policy or RetrievalGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        chunk_count = len(context.retrieved_chunks)
        min_chunks = max(context.min_evidence_chunks, self._policy.min_evidence_chunks)

        if chunk_count == 0:
            return GuardrailResult(
                decision=GuardrailDecision.NO_EVIDENCE,
                allowed=False,
                reason="No evidence chunks were retrieved for this query.",
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

        if chunk_count < min_chunks:
            return GuardrailResult(
                decision=GuardrailDecision.INSUFFICIENT_EVIDENCE,
                allowed=False,
                reason=(
                    f"Retrieval returned {chunk_count} chunk(s), "
                    f"but {min_chunks} are required."
                ),
                confidence=ConfidenceLevel.MEDIUM,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.WEAK_EVIDENCE,
                        message=f"Only {chunk_count} chunk(s) found; minimum required is {min_chunks}.",
                    )
                ],
                safe_user_message=(
                    "Insufficient evidence was found to answer your question reliably."
                ),
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason=f"Retrieval returned {chunk_count} evidence chunk(s).",
            evidence_summary=f"{chunk_count} chunk(s) retrieved.",
        )
