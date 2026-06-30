from __future__ import annotations

from typing import Any

from src.application.guardrails.detectors.grounding_failure_detector import (
    GroundingFailureDetector,
)
from src.application.guardrails.models.guardrail_context import GuardrailContext
from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_result import GuardrailResult
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.models.guardrail_violation import GuardrailViolation
from src.application.guardrails.models.violation_type import ViolationType
from src.application.guardrails.policies.document_grounding_policy import (
    DocumentGroundingPolicy,
)
from src.application.guardrails.services.guardrail_service import GuardrailService


class PreGenerationGuardrailService(GuardrailService):
    def __init__(
        self,
        *,
        policy: DocumentGroundingPolicy | None = None,
        grounding_failure_detector: GroundingFailureDetector | None = None,
        message_builder=None,
    ) -> None:
        super().__init__(message_builder=message_builder)
        self.policy = policy or DocumentGroundingPolicy()
        self.grounding_failure_detector = (
            grounding_failure_detector or GroundingFailureDetector()
        )

    def check(self, context: GuardrailContext) -> GuardrailResult:
        trace = self.create_trace()
        chunks = context.evidence_chunks or context.approved_chunks or context.retrieved_chunks
        if self.policy.require_evidence_for_answers and not chunks:
            result = GuardrailResult(
                decision=GuardrailDecision.SAFE_FALLBACK,
                allowed=False,
                reason="Answer generation requires grounded evidence chunks.",
                severity=GuardrailSeverity.HIGH,
                user_message=self.message_builder.insufficient_evidence_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.GROUNDING_FAILURE,
                        description="Answer generation requires grounded evidence chunks.",
                        policy_name="document_grounding_policy",
                        severity=GuardrailSeverity.HIGH,
                    )
                ],
            )
            return trace.append(
                layer="pre_generation",
                policy="document_grounding_policy",
                result=result,
                route=context.route,
            )

        if self.policy.require_section_or_source_metadata and chunks:
            if not any(_has_source_metadata(chunk) for chunk in chunks):
                result = GuardrailResult(
                    decision=GuardrailDecision.SAFE_FALLBACK,
                    allowed=False,
                    reason="Evidence chunks are missing source metadata required for grounded answer generation.",
                    severity=GuardrailSeverity.MEDIUM,
                    user_message=self.message_builder.insufficient_evidence_message(),
                    violations=[
                        GuardrailViolation(
                            violation_type=ViolationType.GROUNDING_FAILURE,
                            description="Evidence chunks are missing source metadata required for grounded answer generation.",
                            policy_name="document_grounding_policy",
                            severity=GuardrailSeverity.MEDIUM,
                        )
                    ],
                )
                return trace.append(
                    layer="pre_generation",
                    policy="document_grounding_policy",
                    result=result,
                    route=context.route,
                )

        failure = self.grounding_failure_detector.detect(
            answer_text=context.answer_text,
            evidence_chunks=list(chunks),
            selected_document_id=context.selected_document_id,
        )
        if failure.matched:
            result = GuardrailResult(
                decision=GuardrailDecision.SAFE_FALLBACK,
                allowed=False,
                reason=failure.reason or "Grounding failure detected.",
                severity=GuardrailSeverity.HIGH,
                user_message=self.message_builder.grounding_failure_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.GROUNDING_FAILURE,
                        description=failure.reason or "Grounding failure detected.",
                        matched_terms=list(failure.matched_terms),
                        policy_name="document_grounding_policy",
                        severity=GuardrailSeverity.HIGH,
                    )
                ],
            )
            return trace.append(
                layer="pre_generation",
                policy="document_grounding_policy",
                result=result,
                route=context.route,
            )

        result = GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason="Evidence is sufficient for grounded answer generation.",
            severity=GuardrailSeverity.INFO,
        )
        return trace.append(
            layer="pre_generation",
            policy="document_grounding_policy",
            result=result,
            route=context.route,
        )


def _has_source_metadata(chunk: Any) -> bool:
    if isinstance(chunk, dict):
        section_path = chunk.get("section_path")
        source = chunk.get("source")
    else:
        section_path = getattr(chunk, "section_path", None)
        source = getattr(chunk, "source", None)
    if section_path:
        return True
    if source is None:
        return False
    page_start = getattr(source, "page_start", None)
    page_end = getattr(source, "page_end", None)
    return page_start is not None or page_end is not None
