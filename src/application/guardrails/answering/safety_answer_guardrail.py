from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.policies.safety_guardrail_policy import SafetyGuardrailPolicy


class SafetyAnswerGuardrail:
    """Checks that a safety-intent answer (`answer_intent == "safety_warnings"`)
    is backed by enough approved evidence chunks and, if required by policy,
    at least one resolved citation. Warn-only for this first pass, matching
    the rest of the answering guardrails despite the class name and the
    `SAFETY_BLOCKED` decision it returns on failure -- promote to
    `allowed=False` in a future pass once operators have observed the
    real-world false-positive rate on safety-intent answers."""

    def __init__(self, policy: SafetyGuardrailPolicy | None = None) -> None:
        self._policy = policy or SafetyGuardrailPolicy()

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.answer_text is None:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Safety answer validation is not active without an answer to check.",
            )
        if context.answer_intent != "safety_warnings":
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Safety grounding check only applies to safety-intent answers.",
            )
        if not self._policy.block_ungrounded_safety_answers:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Safety grounding check is disabled by policy.",
            )

        violations = []
        if len(context.approved_chunks) < self._policy.min_safety_evidence_chunks:
            violations.append(
                GuardrailViolation(
                    violation_type=ViolationType.SAFETY_CONTENT,
                    description=(
                        f"Safety answer has {len(context.approved_chunks)} approved "
                        f"evidence chunk(s), below the required "
                        f"{self._policy.min_safety_evidence_chunks}."
                    ),
                    policy_name="SafetyGuardrailPolicy.block_ungrounded_safety_answers",
                    field="approved_chunks",
                )
            )

        if self._policy.require_safety_source_citation:
            has_resolved_citation = any(
                note.get("chunk_id") is not None for note in context.reference_notes
            )
            if not has_resolved_citation:
                violations.append(
                    GuardrailViolation(
                        violation_type=ViolationType.SAFETY_CONTENT,
                        description=(
                            "Safety answer has no reference note resolving to a "
                            "cited source."
                        ),
                        policy_name="SafetyGuardrailPolicy.require_safety_source_citation",
                        field="reference_notes",
                    )
                )

        if not violations:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Safety answer check passed.",
            )

        return GuardrailResult(
            decision=GuardrailDecision.SAFETY_BLOCKED,
            allowed=True,
            reason=(
                f"Safety answer failed grounding checks: "
                f"{len(violations)} violation(s) detected."
            ),
            violations=violations,
        )
