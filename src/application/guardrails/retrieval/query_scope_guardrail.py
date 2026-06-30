from __future__ import annotations

from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.detectors import DomainScopeDetector
from src.application.guardrails.messages import GuardrailMessageBuilder
from src.application.guardrails.models.domain_scope_category import DomainScopeCategory
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.policies.enterprise_guardrail_policy import (
    EnterpriseGuardrailPolicy,
)


class QueryScopeGuardrail:
    def __init__(
        self,
        policy: EnterpriseGuardrailPolicy | None = None,
        *,
        detector: DomainScopeDetector | None = None,
        message_builder: GuardrailMessageBuilder | None = None,
    ) -> None:
        self._policy = policy or EnterpriseGuardrailPolicy()
        self._detector = detector or DomainScopeDetector()
        self._message_builder = message_builder or GuardrailMessageBuilder()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        assessment = self._detector.detect(
            context.user_input or context.query_text,
            selected_document_id=context.selected_document_id or context.document_id,
        )
        if (
            assessment.category == DomainScopeCategory.UNKNOWN_AMBIGUOUS
            and assessment.requires_clarification
        ):
            return GuardrailResult(
                decision=GuardrailDecision.NEEDS_CLARIFICATION,
                allowed=False,
                reason=assessment.reason,
                severity=GuardrailSeverity.LOW,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.AMBIGUOUS_QUERY,
                        description=assessment.reason,
                        matched_terms=list(assessment.matched_terms),
                        policy_name="domain_scope_policy",
                        severity=GuardrailSeverity.LOW,
                    )
                ],
                user_message=self._message_builder.missing_document_message(),
            )

        if (
            self._policy.block_out_of_scope_queries
            and assessment.category == DomainScopeCategory.OUT_OF_SCOPE_GENERAL
        ):
            return GuardrailResult(
                decision=GuardrailDecision.OUT_OF_SCOPE,
                allowed=False,
                reason=assessment.reason,
                severity=GuardrailSeverity.LOW,
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.UNRELATED_QUERY,
                        description=assessment.reason,
                        matched_terms=list(assessment.matched_terms),
                        policy_name="domain_scope_policy",
                        severity=GuardrailSeverity.LOW,
                    )
                ],
                user_message=self._message_builder.out_of_scope_message(),
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason=assessment.reason,
        )
