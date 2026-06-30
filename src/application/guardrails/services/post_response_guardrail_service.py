from __future__ import annotations

import re

from src.application.guardrails.detectors import (
    CitationFailureDetector,
    GroundingFailureDetector,
    PromptInjectionDetector,
    SecretLeakageDetector,
)
from src.application.guardrails.models.guardrail_context import GuardrailContext
from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_result import GuardrailResult
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.models.guardrail_violation import GuardrailViolation
from src.application.guardrails.models.violation_type import ViolationType
from src.application.guardrails.policies.citation_policy import CitationPolicy
from src.application.guardrails.policies.document_grounding_policy import (
    DocumentGroundingPolicy,
)
from src.application.guardrails.policies.privacy_policy import PrivacyPolicy
from src.application.guardrails.policies.response_safety_policy import (
    ResponseSafetyPolicy,
)
from src.application.guardrails.services.guardrail_service import GuardrailService

_INTERNAL_ID_RE = re.compile(r"\b(?:doc|chunk|vector)_[A-Za-z0-9_-]+\b")
_WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\[^\s]+")
_NON_GENERATIVE_ROUTES = {
    "blocked_action",
    "out_of_scope",
    "needs_clarification",
    "list_documents",
    "select_document",
    "current_document",
    "clear_document",
    "find_document",
    "document_details",
    "document_exploration",
    "help",
    "exit",
    "quality_gate",
    "retrieval_trace",
}


class PostResponseGuardrailService(GuardrailService):
    def __init__(
        self,
        *,
        citation_policy: CitationPolicy | None = None,
        grounding_policy: DocumentGroundingPolicy | None = None,
        privacy_policy: PrivacyPolicy | None = None,
        response_safety_policy: ResponseSafetyPolicy | None = None,
        citation_failure_detector: CitationFailureDetector | None = None,
        grounding_failure_detector: GroundingFailureDetector | None = None,
        prompt_injection_detector: PromptInjectionDetector | None = None,
        secret_leakage_detector: SecretLeakageDetector | None = None,
        message_builder=None,
    ) -> None:
        super().__init__(message_builder=message_builder)
        self.citation_policy = citation_policy or CitationPolicy()
        self.grounding_policy = grounding_policy or DocumentGroundingPolicy()
        self.privacy_policy = privacy_policy or PrivacyPolicy()
        self.response_safety_policy = response_safety_policy or ResponseSafetyPolicy()
        self.citation_failure_detector = (
            citation_failure_detector or CitationFailureDetector()
        )
        self.grounding_failure_detector = (
            grounding_failure_detector or GroundingFailureDetector()
        )
        self.prompt_injection_detector = (
            prompt_injection_detector or PromptInjectionDetector()
        )
        self.secret_leakage_detector = (
            secret_leakage_detector or SecretLeakageDetector()
        )

    def check(self, context: GuardrailContext) -> tuple[GuardrailResult, str | None]:
        trace = self.create_trace()
        sanitized_answer = self._sanitize_answer(
            context.answer_text,
            debug=context.user_requested_debug,
        )
        evidence_chunks = (
            context.evidence_chunks
            or context.approved_chunks
            or context.retrieved_chunks
            or []
        )
        citations = list(context.citations or [])
        if context.route in _NON_GENERATIVE_ROUTES:
            result = GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Guardrail response route bypasses post-response grounding enforcement.",
                severity=GuardrailSeverity.INFO,
            )
            result = trace.append(
                layer="post_response",
                policy="response_safety_policy",
                result=result,
                route=context.route,
            )
            return result, sanitized_answer
        if not evidence_chunks and not citations:
            result = GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No evidence or citations were attached for post-response grounding checks.",
                severity=GuardrailSeverity.INFO,
            )
            result = trace.append(
                layer="post_response",
                policy="response_safety_policy",
                result=result,
                route=context.route,
            )
            return result, sanitized_answer

        if self.response_safety_policy.block_hidden_prompt_exposure:
            prompt_leak = self.prompt_injection_detector.detect(sanitized_answer or "")
            if prompt_leak.matched:
                result = GuardrailResult(
                    decision=GuardrailDecision.SAFE_FALLBACK,
                    allowed=False,
                    reason=prompt_leak.reason or "Response appears to expose hidden prompt material.",
                    severity=GuardrailSeverity.HIGH,
                    user_message=self.message_builder.prompt_injection_message(),
                    violations=[
                        GuardrailViolation(
                            violation_type=ViolationType.PROMPT_LEAKAGE,
                            description=prompt_leak.reason or "Response appears to expose hidden prompt material.",
                            matched_terms=list(prompt_leak.matched_terms),
                            policy_name="response_safety_policy",
                            severity=GuardrailSeverity.HIGH,
                        )
                    ],
                )
                result = trace.append(
                    layer="post_response",
                    policy="response_safety_policy",
                    result=result,
                    route=context.route,
                )
                return result, result.user_message

        secret_leak = self.secret_leakage_detector.detect(sanitized_answer or "")
        if secret_leak.matched:
            result = GuardrailResult(
                decision=GuardrailDecision.SAFE_FALLBACK,
                allowed=False,
                reason=secret_leak.reason or "Response appears to expose secrets.",
                severity=GuardrailSeverity.CRITICAL,
                user_message=self.message_builder.secret_request_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.SECRET_REQUEST,
                        description=secret_leak.reason or "Response appears to expose secrets.",
                        matched_terms=list(secret_leak.matched_terms),
                        policy_name="privacy_policy",
                        severity=GuardrailSeverity.CRITICAL,
                    )
                ],
            )
            result = trace.append(
                layer="post_response",
                policy="privacy_policy",
                result=result,
                route=context.route,
            )
            return result, result.user_message

        if context.route in self.citation_policy.citation_required_routes and self.citation_policy.require_citations:
            citation_failure = self.citation_failure_detector.detect(
                answer_text=sanitized_answer,
                citations=citations,
            )
            if citation_failure.matched:
                result = GuardrailResult(
                    decision=GuardrailDecision.SAFE_FALLBACK,
                    allowed=False,
                    reason=citation_failure.reason or "Response is missing citations.",
                    severity=GuardrailSeverity.MEDIUM,
                    user_message=self.message_builder.grounding_failure_message(),
                    violations=[
                        GuardrailViolation(
                            violation_type=ViolationType.CITATION_FAILURE,
                            description=citation_failure.reason or "Response is missing citations.",
                            policy_name="citation_policy",
                            severity=GuardrailSeverity.MEDIUM,
                        )
                    ],
                )
                result = trace.append(
                    layer="post_response",
                    policy="citation_policy",
                    result=result,
                    route=context.route,
                )
                return result, result.user_message

        grounding_failure = self.grounding_failure_detector.detect(
            answer_text=sanitized_answer,
            evidence_chunks=evidence_chunks,
            selected_document_id=context.selected_document_id,
        )
        if grounding_failure.matched and self.response_safety_policy.safe_fallback_on_grounding_failure:
            result = GuardrailResult(
                decision=GuardrailDecision.SAFE_FALLBACK,
                allowed=False,
                reason=grounding_failure.reason or "Response could not be grounded confidently.",
                severity=GuardrailSeverity.HIGH,
                user_message=self.message_builder.grounding_failure_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.GROUNDING_FAILURE,
                        description=grounding_failure.reason or "Response could not be grounded confidently.",
                        matched_terms=list(grounding_failure.matched_terms),
                        policy_name="document_grounding_policy",
                        severity=GuardrailSeverity.HIGH,
                    )
                ],
            )
            result = trace.append(
                layer="post_response",
                policy="document_grounding_policy",
                result=result,
                route=context.route,
            )
            return result, result.user_message

        result = GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason="Final response passed guardrail checks.",
            severity=GuardrailSeverity.INFO,
        )
        result = trace.append(
            layer="post_response",
            policy="response_safety_policy",
            result=result,
            route=context.route,
        )
        return result, sanitized_answer

    def _sanitize_answer(self, answer_text: str | None, *, debug: bool) -> str | None:
        if answer_text is None:
            return None
        sanitized = answer_text
        if not debug and self.privacy_policy.redact_internal_ids:
            sanitized = _INTERNAL_ID_RE.sub("[internal-id]", sanitized)
        if not debug and self.privacy_policy.redact_file_paths:
            sanitized = _WINDOWS_PATH_RE.sub("[internal-path]", sanitized)
        return sanitized
