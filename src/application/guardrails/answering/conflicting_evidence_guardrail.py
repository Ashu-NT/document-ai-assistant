from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType

_CLARIFY_MESSAGE = (
    "The sources describing this may refer to different equipment models, "
    "revisions, or configurations, and I don't know which one you mean. "
    "Could you tell me which one, so I can give you a single confident answer?"
)


class ConflictingEvidenceGuardrail:
    """Reads PR 10's `evidence_conflicts` (already computed once during
    evidence assembly, surfaced through `GeneratedAnswer.diagnostics` --
    see `AnswerContextOrganizer.organize()` and `answer_generation_
    service.py`) and decides whether a critical conflict should abstain or
    ask for clarification (PR 11, answering_flow_weakness_remediation_plan.md,
    closes W8; sign-off decision: abstain by default, clarify only when the
    disagreement is demonstrably explained by the conflicting sources
    belonging to different documents -- e.g. different equipment models or
    revisions the user never disambiguated). Never regenerates: a second
    LLM pass over the exact same conflicting evidence is not expected to
    resolve a genuine disagreement."""

    def check(self, context: GuardrailContext) -> GuardrailResult:
        if context.answer_text is None:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="Conflicting-evidence check is not active without an answer to check.",
            )
        conflicts = context.metadata.get("evidence_conflicts") or []
        critical_conflicts = [
            conflict
            for conflict in conflicts
            if isinstance(conflict, dict) and conflict.get("is_critical")
        ]
        if not critical_conflicts:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No conflicting evidence detected.",
            )

        violations = [
            GuardrailViolation(
                violation_type=ViolationType.CONFLICTING_EVIDENCE,
                description=(
                    f"'{conflict.get('key')}' has disagreeing values across "
                    f"sources: {conflict.get('values')}."
                ),
                policy_name="ConflictingEvidenceGuardrail",
                field=conflict.get("field_kind"),
            )
            for conflict in critical_conflicts
        ]

        spans_multiple_documents = any(
            len(set(conflict.get("document_ids") or [])) > 1
            for conflict in critical_conflicts
        )
        if spans_multiple_documents:
            return GuardrailResult(
                decision=GuardrailDecision.NEEDS_CLARIFICATION,
                allowed=True,
                reason=(
                    f"{len(critical_conflicts)} conflict(s) span multiple "
                    "documents -- likely an undisambiguated equipment/"
                    "revision scope, not a genuine same-source disagreement."
                ),
                violations=violations,
                safe_user_message=_CLARIFY_MESSAGE,
            )

        conflict_summary = "; ".join(
            f"{conflict.get('key')} ({' vs '.join(conflict.get('values') or [])})"
            for conflict in critical_conflicts
        )
        return GuardrailResult(
            decision=GuardrailDecision.CONFLICTING_EVIDENCE,
            allowed=True,
            reason=(
                f"{len(critical_conflicts)} critical conflict(s) detected "
                "in the resolved evidence."
            ),
            violations=violations,
            diagnostics={"conflict_summary": conflict_summary},
            safe_user_message=(
                "The sources I found disagree on this: "
                f"{conflict_summary}. I don't want to guess which one is "
                "right, so please check the source document directly."
            ),
        )
