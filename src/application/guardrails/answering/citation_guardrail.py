from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.answer_guardrail_policy import AnswerGuardrailPolicy


class CitationGuardrail:
    """Validates that every reference note the model attributed to a source
    actually resolves to a real source used for this generation (plan
    section 9.6 sections/reference_notes redesign). A reference note with
    `chunk_id is None` means its `source_number` didn't match any source
    actually passed to the model -- a hallucinated citation. Warn-only for
    this first pass: never blocks, only records a violation."""

    def __init__(self, policy: AnswerGuardrailPolicy | None = None) -> None:
        self._policy = policy or AnswerGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.answer_text is None:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Citation validation is not active without an answer to check.",
            )
        if not self._policy.require_citations:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Citation requirement is disabled by policy.",
            )

        unresolved = [
            note
            for note in context.reference_notes
            if note.get("chunk_id") is None
        ]
        if not unresolved:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Citation check passed.",
            )

        violations = [
            GuardrailViolation(
                violation_type=ViolationType.MISSING_CITATION,
                description=(
                    f"Reference note '{note.get('note_id')}' cites source_number "
                    f"{note.get('source_number')}, which does not correspond to "
                    "a source used during answer generation."
                ),
                policy_name="AnswerGuardrailPolicy.require_citations",
                field="reference_notes",
            )
            for note in unresolved
        ]
        return GuardrailResult(
            decision=GuardrailDecision.CITATION_REQUIRED,
            allowed=True,
            reason=(
                f"{len(unresolved)} reference note(s) cite an unresolved "
                "source_number."
            ),
            violations=violations,
        )
