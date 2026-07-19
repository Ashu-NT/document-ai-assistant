from src.application.contracts.guardrails import GuardrailDecision
from src.application.guardrails.answering.post_answer_abstain_messages import (
    _DEFAULT_ABSTAIN_MESSAGE,
    _IMMEDIATE_ABSTAIN_MESSAGES,
    _REGENERATE_ESCALATED_ABSTAIN_MESSAGES,
    resolve_abstain_message,
)
from src.application.guardrails.messages.guardrail_message_builder import (
    GuardrailMessageBuilder,
)
from src.application.guardrails.models.guardrail_result import GuardrailResult
from src.application.langgraph.reflection.constants import (
    REFLECTION_SAFE_FAILURE_MESSAGE,
)


def _result(decision: GuardrailDecision, safe_user_message: str | None = None) -> GuardrailResult:
    return GuardrailResult(
        decision=decision,
        allowed=True,
        reason="test",
        safe_user_message=safe_user_message,
    )


def test_prefers_the_guardrails_own_message_when_present() -> None:
    result = _result(GuardrailDecision.CONFLICTING_EVIDENCE, "Custom message.")

    assert resolve_abstain_message(result, regenerated=True) == "Custom message."


def test_falls_back_to_the_regenerate_escalated_template() -> None:
    result = _result(GuardrailDecision.CITATION_REQUIRED)

    message = resolve_abstain_message(result, regenerated=True)

    assert "even after trying again" in message


def test_falls_back_to_the_immediate_abstain_template_for_safety() -> None:
    result = _result(GuardrailDecision.SAFETY_BLOCKED)

    message = resolve_abstain_message(result, regenerated=False)

    assert "safety" in message.lower()
    assert "even after trying again" not in message


def test_returns_the_default_message_for_none_result() -> None:
    assert resolve_abstain_message(None, regenerated=True)


def test_returns_the_default_message_for_an_unmapped_decision() -> None:
    result = _result(GuardrailDecision.OUT_OF_SCOPE)

    message = resolve_abstain_message(result, regenerated=False)

    assert message == (
        "I could not produce a confidently grounded answer to this, so I'm "
        "holding back rather than guess. Please check the source document "
        "directly."
    )


def test_no_abstain_message_collides_with_the_recovery_heuristics_sentinels() -> None:
    """FinalResponseNode's recovery heuristic (`_is_safe_failure_message()`)
    is an exact-string match against exactly 2 known sentinels. None of
    PR 11's own abstain messages may equal either one -- otherwise a PR 11
    abstain could be mistaken for reflection's own safe-failure text and
    get silently swapped back to the original ungrounded answer (the exact
    bug `answering_flow_weakness_remediation_plan.md`'s PR 11 note warns
    about)."""
    sentinels = {
        REFLECTION_SAFE_FAILURE_MESSAGE.strip(),
        GuardrailMessageBuilder().grounding_failure_message().strip(),
    }
    all_messages = [
        _DEFAULT_ABSTAIN_MESSAGE,
        *_REGENERATE_ESCALATED_ABSTAIN_MESSAGES.values(),
        *_IMMEDIATE_ABSTAIN_MESSAGES.values(),
    ]
    for message in all_messages:
        assert message.strip() not in sentinels
