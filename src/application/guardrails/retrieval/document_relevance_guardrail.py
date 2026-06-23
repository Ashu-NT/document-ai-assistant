from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.retrieval_guardrail_policy import (
    RetrievalGuardrailPolicy,
)

_SAFETY_INTENT = "safety"


class DocumentRelevanceGuardrail:
    def __init__(self, policy: RetrievalGuardrailPolicy | None = None) -> None:
        self._policy = policy or RetrievalGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if not context.query_chunk_types or not context.retrieved_chunks:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No chunk-type constraints to validate against.",
            )

        requested_types = frozenset(context.query_chunk_types)
        matched_chunks = [
            chunk
            for chunk in context.retrieved_chunks
            if chunk.chunk_type.value in requested_types
        ]

        if matched_chunks:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason=(
                    f"{len(matched_chunks)} chunk(s) match the requested chunk types."
                ),
                evidence_summary=f"{len(matched_chunks)} relevant chunk(s) found.",
            )

        is_safety_intent = context.query_intent == _SAFETY_INTENT
        if is_safety_intent:
            return GuardrailResult(
                decision=GuardrailDecision.SAFETY_BLOCKED,
                allowed=False,
                reason=(
                    "No safety-classified evidence found. "
                    "Safety information must be grounded in documented sources."
                ),
                confidence=ConfidenceLevel.HIGH,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.SAFETY_CONTENT,
                        message=(
                            "No chunks matching safety chunk types were retrieved. "
                            "Ungrounded safety answers are not permitted."
                        ),
                    )
                ],
                safe_user_message=(
                    "Safety-critical information requires verified documentation. "
                    "No matching safety content was found. "
                    "Please consult the original equipment manual directly."
                ),
            )

        return GuardrailResult(
            decision=GuardrailDecision.INSUFFICIENT_EVIDENCE,
            allowed=False,
            reason=(
                f"No chunks matching the requested types "
                f"({', '.join(sorted(requested_types))}) were retrieved."
            ),
            confidence=ConfidenceLevel.MEDIUM,
            violations=[
                GuardrailViolation(
                    violation_type=ViolationType.IRRELEVANT_CHUNKS,
                    message=(
                        f"Retrieved chunks do not match requested types: "
                        f"{', '.join(sorted(requested_types))}."
                    ),
                )
            ],
            safe_user_message=(
                "The retrieved documents do not contain the specific type of "
                "information requested."
            ),
        )
