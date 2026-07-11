from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.answer_guardrail_policy import AnswerGuardrailPolicy


class AnswerSupportGuardrail:
    """Scores the overall fraction of a structured answer that is backed by
    a resolved reference note (plan section 9.6 sections/reference_notes
    redesign) -- distinct from `CitationGuardrail` (resolves individual
    reference notes) and `UnsupportedClaimGuardrail` (flags individual
    sections with zero reference notes). This guardrail instead computes
    one overall support ratio across the whole answer. Warn-only for this
    first pass: never blocks, only records a violation."""

    def __init__(self, policy: AnswerGuardrailPolicy | None = None) -> None:
        self._policy = policy or AnswerGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.answer_text is None:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Answer support validation is not active without an answer to check.",
            )

        if context.sections:
            resolved_note_ids = {
                note.get("note_id")
                for note in context.reference_notes
                if note.get("chunk_id") is not None
            }
            supported_count = sum(
                1
                for section in context.sections
                if section.get("reference_note_ids")
                and any(
                    note_id in resolved_note_ids
                    for note_id in section.get("reference_note_ids") or []
                )
            )
            score = supported_count / len(context.sections)
            field = "sections"
        elif context.reference_notes:
            resolved_count = sum(
                1
                for note in context.reference_notes
                if note.get("chunk_id") is not None
            )
            score = resolved_count / len(context.reference_notes)
            field = "reference_notes"
        else:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Answer support validation is not active without a structured breakdown to score.",
            )

        if score < self._policy.min_claim_support_score:
            violations = [
                GuardrailViolation(
                    violation_type=ViolationType.WEAK_EVIDENCE,
                    description=(
                        f"Answer support score {score:.2f} is below the "
                        f"{self._policy.min_claim_support_score} threshold."
                    ),
                    policy_name="AnswerGuardrailPolicy.min_claim_support_score",
                    field=field,
                )
            ]
            return GuardrailResult(
                decision=GuardrailDecision.INSUFFICIENT_EVIDENCE,
                allowed=True,
                reason=(
                    f"Answer support score {score:.2f} is below the "
                    f"{self._policy.min_claim_support_score} threshold."
                ),
                violations=violations,
                diagnostics={"support_score": score},
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason="Answer support check passed.",
            diagnostics={"support_score": score},
        )
