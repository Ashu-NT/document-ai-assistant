from src.application.contracts.guardrails.confidence_level import ConfidenceLevel
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType


class ScopedDocumentConsistencyGuardrail:
    def check(self, context: GuardrailContext) -> GuardrailResult:
        scoped_document_id = context.document_id
        if not scoped_document_id:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No scoped document was requested.",
            )

        chunks = context.approved_chunks or context.retrieved_chunks
        if not chunks:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No chunks available for document-scope validation.",
            )

        approved_ids: list[str] = []
        rejected_ids: list[str] = []
        violations: list[GuardrailViolation] = []

        for chunk in chunks:
            if chunk.document_id == scoped_document_id:
                approved_ids.append(chunk.chunk_id)
                continue

            rejected_ids.append(chunk.chunk_id)
            violations.append(
                GuardrailViolation(
                    violation_type=ViolationType.IRRELEVANT_CHUNKS,
                    message=(
                        "Chunk document_id does not match the selected document scope."
                    ),
                    chunk_id=chunk.chunk_id,
                )
            )

        if not rejected_ids:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="All chunks match the selected document scope.",
                approved_chunk_ids=approved_ids,
            )

        if not approved_ids:
            return GuardrailResult(
                decision=GuardrailDecision.INSUFFICIENT_EVIDENCE,
                allowed=False,
                reason="All retrieved chunks were outside the selected document scope.",
                confidence=ConfidenceLevel.HIGH,
                violations=violations,
                rejected_chunk_ids=rejected_ids,
                safe_user_message=(
                    "No evidence remained after enforcing the selected document scope."
                ),
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW_WITH_CAUTION,
            allowed=True,
            reason=(
                f"{len(approved_ids)} chunk(s) match the selected document scope; "
                f"{len(rejected_ids)} chunk(s) were rejected."
            ),
            confidence=ConfidenceLevel.HIGH,
            violations=violations,
            approved_chunk_ids=approved_ids,
            rejected_chunk_ids=rejected_ids,
            evidence_summary=(
                f"Document scope enforcement removed {len(rejected_ids)} chunk(s)."
            ),
        )
