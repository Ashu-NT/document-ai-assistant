from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.answer_guardrail_policy import AnswerGuardrailPolicy

_PRESCRIPTIVE_ANSWER_INTENTS = frozenset(
    {
        "procedure_steps",
        "maintenance_summary",
        "specification_summary",
        "troubleshooting",
    }
)


class UnsupportedSuggestionGuardrail:
    """Detects sections of a prescriptive answer (procedure steps,
    maintenance/specification summaries, troubleshooting) that carry no
    supporting reference notes -- a possible invented recommendation or
    procedure. Distinct from `UnsupportedClaimGuardrail`, which flags the
    same shape of gap for every answer intent; this guardrail is scoped to
    only the prescriptive intents and returns a different decision/violation
    type so the two are distinguishable in diagnostics. Warn-only for this
    first pass: never blocks, only records a violation."""

    def __init__(self, policy: AnswerGuardrailPolicy | None = None) -> None:
        self._policy = policy or AnswerGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.answer_text is None:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Suggestion detection is not active without an answer to check.",
            )
        if not self._policy.block_unsupported_suggestions:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Suggestion detection is disabled by policy.",
            )
        if context.answer_intent not in _PRESCRIPTIVE_ANSWER_INTENTS:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Suggestion detection only applies to prescriptive answer intents.",
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
                reason="No unsupported suggestions detected.",
            )

        violations = [
            GuardrailViolation(
                violation_type=ViolationType.GROUNDING_FAILURE,
                description=(
                    f"Section '{section.get('heading')}' has no reference notes "
                    "supporting its content -- possible invented recommendation "
                    "or procedure."
                ),
                policy_name="AnswerGuardrailPolicy.block_unsupported_suggestions",
                field="sections",
            )
            for section in unsupported
        ]
        return GuardrailResult(
            decision=GuardrailDecision.ALLOW_WITH_CAUTION,
            allowed=True,
            reason=(
                f"{len(unsupported)} section(s) of this prescriptive answer have "
                "no supporting reference notes."
            ),
            violations=violations,
        )
