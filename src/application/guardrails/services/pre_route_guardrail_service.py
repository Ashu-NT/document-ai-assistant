from __future__ import annotations

from src.application.guardrails.detectors import (
    DomainScopeDetector,
    PromptInjectionDetector,
    SecretLeakageDetector,
    ToolAbuseDetector,
    UnsafeActionDetector,
)
from src.application.guardrails.models.domain_scope_category import DomainScopeCategory
from src.application.guardrails.models.guardrail_context import GuardrailContext
from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_result import GuardrailResult
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.models.guardrail_violation import GuardrailViolation
from src.application.guardrails.models.violation_type import ViolationType
from src.application.guardrails.services.guardrail_service import GuardrailService


class PreRouteGuardrailService(GuardrailService):
    def __init__(
        self,
        *,
        domain_scope_detector: DomainScopeDetector | None = None,
        unsafe_action_detector: UnsafeActionDetector | None = None,
        prompt_injection_detector: PromptInjectionDetector | None = None,
        secret_leakage_detector: SecretLeakageDetector | None = None,
        tool_abuse_detector: ToolAbuseDetector | None = None,
        message_builder=None,
    ) -> None:
        super().__init__(message_builder=message_builder)
        self.domain_scope_detector = domain_scope_detector or DomainScopeDetector()
        self.unsafe_action_detector = unsafe_action_detector or UnsafeActionDetector()
        self.prompt_injection_detector = (
            prompt_injection_detector or PromptInjectionDetector()
        )
        self.secret_leakage_detector = (
            secret_leakage_detector or SecretLeakageDetector()
        )
        self.tool_abuse_detector = tool_abuse_detector or ToolAbuseDetector()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        trace = self.create_trace()
        user_input = context.user_input or context.query_text

        unsafe = self.unsafe_action_detector.detect(user_input)
        if unsafe.is_unsafe:
            result = GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                allowed=False,
                reason=unsafe.reason or "Unsafe destructive request.",
                severity=unsafe.severity,
                user_message=self.message_builder.unsafe_destructive_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.UNSAFE_DESTRUCTIVE,
                        description=unsafe.reason or "Unsafe destructive request.",
                        matched_terms=list(unsafe.matched_terms),
                        policy_name="unsafe_action_policy",
                        severity=unsafe.severity,
                    )
                ],
                diagnostics={"scope_category": DomainScopeCategory.UNSAFE_DESTRUCTIVE.value},
            )
            return trace.append(
                layer="pre_route",
                policy="unsafe_action_policy",
                result=result,
                route=context.route,
            )

        injection = self.prompt_injection_detector.detect(user_input)
        if injection.matched:
            result = GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                allowed=False,
                reason=injection.reason or "Prompt injection request detected.",
                severity=injection.severity,
                user_message=self.message_builder.prompt_injection_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.PROMPT_INJECTION,
                        description=injection.reason or "Prompt injection request detected.",
                        matched_terms=list(injection.matched_terms),
                        policy_name="prompt_injection_policy",
                        severity=injection.severity,
                    )
                ],
                diagnostics={"scope_category": DomainScopeCategory.PROMPT_INJECTION.value},
            )
            return trace.append(
                layer="pre_route",
                policy="prompt_injection_policy",
                result=result,
                route=context.route,
            )

        secret_request = self.secret_leakage_detector.detect(user_input)
        if secret_request.matched:
            result = GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                allowed=False,
                reason=secret_request.reason or "Secret request detected.",
                severity=secret_request.severity,
                user_message=self.message_builder.secret_request_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.SECRET_REQUEST,
                        description=secret_request.reason or "Secret request detected.",
                        matched_terms=list(secret_request.matched_terms),
                        policy_name="privacy_policy",
                        severity=secret_request.severity,
                    )
                ],
                diagnostics={"scope_category": DomainScopeCategory.SECRET_REQUEST.value},
            )
            return trace.append(
                layer="pre_route",
                policy="privacy_policy",
                result=result,
                route=context.route,
            )

        tool_abuse = self.tool_abuse_detector.detect(user_input)
        if tool_abuse.matched:
            result = GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                allowed=False,
                reason=tool_abuse.reason or "Tool abuse request detected.",
                severity=tool_abuse.severity,
                user_message=self.message_builder.tool_abuse_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.TOOL_ABUSE,
                        description=tool_abuse.reason or "Tool abuse request detected.",
                        matched_terms=list(tool_abuse.matched_terms),
                        policy_name="tool_execution_policy",
                        severity=tool_abuse.severity,
                    )
                ],
                diagnostics={"scope_category": "tool_abuse"},
            )
            return trace.append(
                layer="pre_route",
                policy="tool_execution_policy",
                result=result,
                route=context.route,
            )

        assessment = self.domain_scope_detector.detect(
            user_input,
            selected_document_id=context.selected_document_id,
        )
        if assessment.category == DomainScopeCategory.OUT_OF_SCOPE_GENERAL:
            result = GuardrailResult(
                decision=GuardrailDecision.REDIRECT,
                allowed=False,
                reason=assessment.reason,
                severity=GuardrailSeverity.LOW,
                user_message=self.message_builder.out_of_scope_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.UNRELATED_QUERY,
                        description=assessment.reason,
                        matched_terms=list(assessment.matched_terms),
                        policy_name="domain_scope_policy",
                        severity=GuardrailSeverity.LOW,
                    )
                ],
                diagnostics={"scope_category": assessment.category.value},
            )
            return trace.append(
                layer="pre_route",
                policy="domain_scope_policy",
                result=result,
                route=context.route,
            )

        if assessment.category == DomainScopeCategory.UNKNOWN_AMBIGUOUS and assessment.requires_clarification:
            result = GuardrailResult(
                decision=GuardrailDecision.CLARIFY,
                allowed=False,
                reason=assessment.reason,
                severity=GuardrailSeverity.LOW,
                user_message=self.message_builder.missing_document_message(),
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.AMBIGUOUS_QUERY,
                        description=assessment.reason,
                        matched_terms=list(assessment.matched_terms),
                        policy_name="domain_scope_policy",
                        severity=GuardrailSeverity.LOW,
                    )
                ],
                diagnostics={"scope_category": assessment.category.value},
            )
            return trace.append(
                layer="pre_route",
                policy="domain_scope_policy",
                result=result,
                route=context.route,
            )

        result = GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason=assessment.reason,
            severity=GuardrailSeverity.INFO,
            diagnostics={"scope_category": assessment.category.value},
        )
        return trace.append(
            layer="pre_route",
            policy="domain_scope_policy",
            result=result,
            route=context.route,
        )
