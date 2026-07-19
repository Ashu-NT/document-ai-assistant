from __future__ import annotations

from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_disposition import (
    GuardrailDisposition,
)
from src.application.guardrails.models.guardrail_result import GuardrailResult

_SEVERITY_ORDER: dict[GuardrailDisposition, int] = {
    GuardrailDisposition.PASS: 0,
    GuardrailDisposition.WARN: 1,
    GuardrailDisposition.REGENERATE: 2,
    GuardrailDisposition.CLARIFY: 3,
    GuardrailDisposition.ABSTAIN: 4,
    GuardrailDisposition.BLOCK: 5,
}

# Scoped to the 5 post-answer guardrails' own "failure" decision values
# (each unique to the guardrail that returns it) plus
# ConflictingEvidenceGuardrail's two outcomes -- PR 11,
# answering_flow_weakness_remediation_plan.md, closes W8. Approved
# severity tiering:
#   - CitationGuardrail / UnsupportedClaimGuardrail /
#     UnsupportedSuggestionGuardrail / AnswerSupportGuardrail -> REGENERATE
#     once, then ABSTAIN if the regenerated answer still fails (handled by
#     the pipeline's regenerate-once loop, not this mapping).
#   - SafetyAnswerGuardrail -> ABSTAIN immediately, no regenerate: retrying
#     a failed safety-evidence check risks confidently generating a
#     *different* wrong answer about safety-critical content.
#   - ConflictingEvidenceGuardrail -> ABSTAIN by default; CLARIFY only when
#     the conflict spans multiple documents (see
#     conflicting_evidence_guardrail.py).
# Any decision not listed here (including every context/pre-generation/
# final-response-stage decision, which already correctly blocks via
# `allowed=False` before this mapper ever sees it) defaults to WARN --
# today's behavior, unchanged, for anything this PR doesn't explicitly
# escalate.
_POST_ANSWER_DISPOSITION_BY_DECISION: dict[GuardrailDecision, GuardrailDisposition] = {
    GuardrailDecision.ALLOW: GuardrailDisposition.PASS,
    GuardrailDecision.CITATION_REQUIRED: GuardrailDisposition.REGENERATE,
    GuardrailDecision.UNSUPPORTED_CLAIMS: GuardrailDisposition.REGENERATE,
    GuardrailDecision.ALLOW_WITH_CAUTION: GuardrailDisposition.REGENERATE,
    GuardrailDecision.INSUFFICIENT_EVIDENCE: GuardrailDisposition.REGENERATE,
    GuardrailDecision.SAFETY_BLOCKED: GuardrailDisposition.ABSTAIN,
    GuardrailDecision.CONFLICTING_EVIDENCE: GuardrailDisposition.ABSTAIN,
    GuardrailDecision.NEEDS_CLARIFICATION: GuardrailDisposition.CLARIFY,
}


def map_post_answer_disposition(result: GuardrailResult) -> GuardrailDisposition:
    # `allowed=False` is an unconditional hard block regardless of decision
    # value -- preserves the pre-PR-11 contract (any guardrail that already
    # sets allowed=False must keep blocking immediately) as a strict
    # override on top of the new graduated tiers below, which only apply
    # to today's warn-only (allowed=True) post-answer guardrails.
    if not result.allowed:
        return GuardrailDisposition.BLOCK
    return _POST_ANSWER_DISPOSITION_BY_DECISION.get(
        result.decision, GuardrailDisposition.WARN
    )


def combine_post_answer_dispositions(
    results: list[GuardrailResult],
) -> tuple[GuardrailDisposition, GuardrailResult | None]:
    """The single most-severe disposition across every post-answer
    guardrail result for this turn, plus the result that drove it (used
    to build the abstain/clarify user-facing message). `None`/PASS for an
    empty result list -- nothing ran, nothing to escalate."""
    if not results:
        return GuardrailDisposition.PASS, None
    ranked = sorted(
        ((map_post_answer_disposition(result), result) for result in results),
        key=lambda pair: _SEVERITY_ORDER[pair[0]],
        reverse=True,
    )
    return ranked[0]
