from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.answer_guardrail_policy import AnswerGuardrailPolicy


class UnsupportedClaimGuardrail:
    """Detects sections of a structured answer that carry no supporting
    reference notes (plan section 9.6 sections/reference_notes redesign).
    A section with an empty `reference_note_ids` list is a substantive
    claim with zero recorded grounding. Warn-only for this first pass:
    never blocks, only records a violation."""

    def __init__(self, policy: AnswerGuardrailPolicy | None = None) -> None:
        self._policy = policy or AnswerGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.answer_text is None:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Unsupported claim detection is not active without an answer to check.",
            )
        if not self._policy.block_unsupported_claims:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Unsupported claim detection is disabled by policy.",
            )

        unsupported = [
            section
            for section in context.sections
            if not section.get("reference_note_ids")
        ]
        if not unsupported:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No unsupported claims detected.",
            )

        violations = [
            GuardrailViolation(
                violation_type=ViolationType.UNSUPPORTED_CLAIM,
                description=(
                    f"Section '{section.get('heading')}' has no reference "
                    "notes supporting its content."
                ),
                policy_name="AnswerGuardrailPolicy.block_unsupported_claims",
                field="sections",
            )
            for section in unsupported
        ]
        return GuardrailResult(
            decision=GuardrailDecision.UNSUPPORTED_CLAIMS,
            allowed=True,
            reason=(
                f"{len(unsupported)} section(s) have no supporting reference "
                "notes."
            ),
            violations=violations,
        )
