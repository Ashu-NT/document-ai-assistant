from src.application.contracts.guardrails import GuardrailDecision
from src.application.guardrails.answering.guardrail_disposition_mapper import (
    combine_post_answer_dispositions,
    map_post_answer_disposition,
)
from src.application.guardrails.models.guardrail_disposition import (
    GuardrailDisposition,
)
from src.application.guardrails.models.guardrail_result import GuardrailResult


def _result(decision: GuardrailDecision, allowed: bool = True) -> GuardrailResult:
    return GuardrailResult(decision=decision, allowed=allowed, reason="test")


def test_map_post_answer_disposition_for_each_approved_tier() -> None:
    assert map_post_answer_disposition(_result(GuardrailDecision.ALLOW)) == (
        GuardrailDisposition.PASS
    )
    assert map_post_answer_disposition(_result(GuardrailDecision.CITATION_REQUIRED)) == (
        GuardrailDisposition.REGENERATE
    )
    assert map_post_answer_disposition(_result(GuardrailDecision.UNSUPPORTED_CLAIMS)) == (
        GuardrailDisposition.REGENERATE
    )
    assert map_post_answer_disposition(_result(GuardrailDecision.ALLOW_WITH_CAUTION)) == (
        GuardrailDisposition.REGENERATE
    )
    assert map_post_answer_disposition(_result(GuardrailDecision.INSUFFICIENT_EVIDENCE)) == (
        GuardrailDisposition.REGENERATE
    )
    assert map_post_answer_disposition(_result(GuardrailDecision.SAFETY_BLOCKED)) == (
        GuardrailDisposition.ABSTAIN
    )
    assert map_post_answer_disposition(_result(GuardrailDecision.CONFLICTING_EVIDENCE)) == (
        GuardrailDisposition.ABSTAIN
    )
    assert map_post_answer_disposition(_result(GuardrailDecision.NEEDS_CLARIFICATION)) == (
        GuardrailDisposition.CLARIFY
    )


def test_map_post_answer_disposition_defaults_to_warn_for_unmapped_decisions() -> None:
    assert map_post_answer_disposition(_result(GuardrailDecision.OUT_OF_SCOPE)) == (
        GuardrailDisposition.WARN
    )


def test_map_post_answer_disposition_treats_allowed_false_as_an_unconditional_block() -> None:
    """Preserves the pre-PR-11 contract: any guardrail that already sets
    allowed=False must keep blocking immediately, regardless of what its
    decision value would otherwise map to (even a decision this PR
    escalates only to REGENERATE)."""
    result = _result(GuardrailDecision.CITATION_REQUIRED, allowed=False)

    assert map_post_answer_disposition(result) == GuardrailDisposition.BLOCK


def test_combine_returns_pass_for_an_empty_result_list() -> None:
    disposition, driving_result = combine_post_answer_dispositions([])

    assert disposition == GuardrailDisposition.PASS
    assert driving_result is None


def test_combine_picks_the_single_most_severe_disposition() -> None:
    results = [
        _result(GuardrailDecision.ALLOW),
        _result(GuardrailDecision.CITATION_REQUIRED),
        _result(GuardrailDecision.SAFETY_BLOCKED),
    ]

    disposition, driving_result = combine_post_answer_dispositions(results)

    assert disposition == GuardrailDisposition.ABSTAIN
    assert driving_result.decision == GuardrailDecision.SAFETY_BLOCKED


def test_combine_prefers_clarify_over_regenerate() -> None:
    results = [
        _result(GuardrailDecision.CITATION_REQUIRED),
        _result(GuardrailDecision.NEEDS_CLARIFICATION),
    ]

    disposition, driving_result = combine_post_answer_dispositions(results)

    assert disposition == GuardrailDisposition.CLARIFY
    assert driving_result.decision == GuardrailDecision.NEEDS_CLARIFICATION


def test_combine_returns_pass_when_every_result_passes() -> None:
    results = [_result(GuardrailDecision.ALLOW), _result(GuardrailDecision.ALLOW)]

    disposition, driving_result = combine_post_answer_dispositions(results)

    assert disposition == GuardrailDisposition.PASS
