from __future__ import annotations

from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_result import GuardrailResult

# Draft copy for PR 11 (answering_flow_weakness_remediation_plan.md, closes
# W8) -- reviewed here rather than nailed down before implementation, per
# the sign-off conversation. A guardrail's own `safe_user_message` (set by
# ConflictingEvidenceGuardrail and, once written, SafetyAnswerGuardrail)
# always wins over these generic templates -- see `resolve_abstain_message()`.
_REGENERATE_ESCALATED_ABSTAIN_MESSAGES: dict[GuardrailDecision, str] = {
    GuardrailDecision.CITATION_REQUIRED: (
        "I found information, but I could not verify all of the citations "
        "behind this answer, even after trying again, so I'm holding back "
        "rather than risk an unverified claim. Please check the source "
        "document directly."
    ),
    GuardrailDecision.UNSUPPORTED_CLAIMS: (
        "Part of this answer isn't backed by a specific citation I can "
        "verify, even after trying again, so I'm holding back rather than "
        "risk an unsupported claim. Please check the source document "
        "directly."
    ),
    GuardrailDecision.ALLOW_WITH_CAUTION: (
        "This answer includes a recommendation I could not verify against "
        "a specific source, even after trying again, so I'm holding back "
        "rather than risk suggesting something unsupported. Please check "
        "the source document directly."
    ),
    GuardrailDecision.INSUFFICIENT_EVIDENCE: (
        "I could not find enough supporting evidence to confidently answer "
        "this, even after trying again, so I'm holding back rather than "
        "guess. Please check the source document directly."
    ),
}

_IMMEDIATE_ABSTAIN_MESSAGES: dict[GuardrailDecision, str] = {
    GuardrailDecision.SAFETY_BLOCKED: (
        "I could not verify this safety information against a specific, "
        "citable source, so I'm not going to guess. Please consult the "
        "source document's safety section directly."
    ),
}

_DEFAULT_ABSTAIN_MESSAGE = (
    "I could not produce a confidently grounded answer to this, so I'm "
    "holding back rather than guess. Please check the source document "
    "directly."
)


def resolve_abstain_message(
    result: GuardrailResult | None,
    *,
    regenerated: bool,
) -> str:
    """The user-facing message for an ABSTAIN disposition. A guardrail that
    already built its own `safe_user_message` (ConflictingEvidenceGuardrail
    today) always wins; otherwise falls back to a generic template keyed
    on the driving decision and whether a regenerate attempt already ran."""
    if result is None:
        return _DEFAULT_ABSTAIN_MESSAGE
    if result.safe_user_message:
        return result.safe_user_message
    table = (
        _REGENERATE_ESCALATED_ABSTAIN_MESSAGES
        if regenerated
        else _IMMEDIATE_ABSTAIN_MESSAGES
    )
    return table.get(result.decision, _DEFAULT_ABSTAIN_MESSAGE)
