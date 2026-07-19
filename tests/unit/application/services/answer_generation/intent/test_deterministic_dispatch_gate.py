from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.intent.answer_intent_decision import (
    AnswerIntentDecision,
)
from src.application.services.answer_generation.intent.deterministic_dispatch_gate import (
    DeterministicDispatchGate,
)


def _decision(**overrides) -> AnswerIntentDecision:
    defaults = dict(
        intent=AnswerIntent.IDENTIFIER_LOOKUP,
        confidence=0.9,
        reason="test",
        matched_signals=["question:part number"],
        runner_up_intent=None,
        runner_up_score=0,
        best_score=6,
    )
    defaults.update(overrides)
    return AnswerIntentDecision(**defaults)


def test_bypasses_for_a_contested_intent_decision() -> None:
    gate = DeterministicDispatchGate()
    decision = _decision(
        intent=AnswerIntent.IDENTIFIER_LOOKUP,
        best_score=6,
        runner_up_intent=AnswerIntent.TABLE_SUMMARY,
        runner_up_score=6,
    )

    result = gate.evaluate(
        question="List all part numbers",
        effective_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        intent_decision=decision,
    )

    assert result.should_bypass is True
    assert result.reason == "contested_intent"
    assert result.margin == 0


def test_bypasses_for_a_compound_question_even_when_not_contested() -> None:
    gate = DeterministicDispatchGate()
    decision = _decision(intent=AnswerIntent.IDENTIFIER_LOOKUP)

    result = gate.evaluate(
        question="What are the spare parts and how do I replace the seal?",
        effective_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        intent_decision=decision,
    )

    assert result.should_bypass is True
    assert result.reason == "compound_question"
    assert result.compound_intent_value == AnswerIntent.PROCEDURE_STEPS.value


def test_does_not_bypass_for_a_clear_non_compound_question() -> None:
    gate = DeterministicDispatchGate()
    decision = _decision(intent=AnswerIntent.IDENTIFIER_LOOKUP)

    result = gate.evaluate(
        question="List all part numbers.",
        effective_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        intent_decision=decision,
    )

    assert result.should_bypass is False
    assert result.reason is None


def test_contested_check_runs_before_the_compound_check() -> None:
    """Both conditions can independently trigger a bypass -- a contested
    decision must report itself as the reason even if the question also
    happens to look compound, since that's the cheaper/first check."""
    gate = DeterministicDispatchGate()
    decision = _decision(
        intent=AnswerIntent.IDENTIFIER_LOOKUP,
        best_score=6,
        runner_up_intent=AnswerIntent.TABLE_SUMMARY,
        runner_up_score=6,
    )

    result = gate.evaluate(
        question="What are the spare parts and how do I replace the seal?",
        effective_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        intent_decision=decision,
    )

    assert result.reason == "contested_intent"


def test_bypasses_for_a_decision_with_no_matched_signal_at_all() -> None:
    """PR 5 (answering_flow_weakness_remediation_plan.md): a pure fallback
    winner (empty matched_signals -- see AnswerIntentAnalyzer.analyze()'s
    scores[best_intent] <= 0 branch) is exactly as risky as a contested
    tie, just from the opposite direction: nothing positively chose this
    intent, so a domain-specific renderer must not fire on the strength of
    a default."""
    gate = DeterministicDispatchGate()
    decision = _decision(
        intent=AnswerIntent.IDENTIFIER_LOOKUP,
        matched_signals=[],
        runner_up_intent=None,
    )

    result = gate.evaluate(
        question="Tell me about the pump.",
        effective_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        intent_decision=decision,
    )

    assert result.should_bypass is True
    assert result.reason == "no_signal"


def test_ignores_a_no_signal_decision_about_an_intent_that_was_overridden_away() -> None:
    gate = DeterministicDispatchGate()
    decision = _decision(
        intent=AnswerIntent.IDENTIFIER_LOOKUP,
        matched_signals=[],
        runner_up_intent=None,
    )

    result = gate.evaluate(
        question="Tell me about the pump.",
        effective_intent=AnswerIntent.PROCEDURE_STEPS,
        intent_decision=decision,
    )

    assert result.should_bypass is False


def test_contested_check_runs_before_the_no_signal_check() -> None:
    gate = DeterministicDispatchGate()
    decision = _decision(
        intent=AnswerIntent.IDENTIFIER_LOOKUP,
        matched_signals=[],
        best_score=6,
        runner_up_intent=AnswerIntent.TABLE_SUMMARY,
        runner_up_score=6,
    )

    result = gate.evaluate(
        question="List all part numbers",
        effective_intent=AnswerIntent.IDENTIFIER_LOOKUP,
        intent_decision=decision,
    )

    assert result.reason == "contested_intent"


def test_ignores_a_contested_tie_about_an_intent_that_was_overridden_away() -> None:
    """Regression test: a caller can force `effective_intent` to something
    other than what AnswerIntentAnalyzer.analyze() would pick on its own
    (e.g. "How do I troubleshoot a pump that does not start?" naturally
    ties PROCEDURE_STEPS/TROUBLESHOOTING, but the caller already resolved
    this turn to TROUBLESHOOTING through a different path). The analyzer's
    own tie is about a hypothetical intent that was never actually used,
    so it must not block dispatch for the intent that IS in effect."""
    gate = DeterministicDispatchGate()
    decision = _decision(
        intent=AnswerIntent.PROCEDURE_STEPS,
        best_score=6,
        runner_up_intent=AnswerIntent.TROUBLESHOOTING,
        runner_up_score=6,
    )

    result = gate.evaluate(
        question="How do I troubleshoot a pump that does not start?",
        effective_intent=AnswerIntent.TROUBLESHOOTING,
        intent_decision=decision,
    )

    assert result.should_bypass is False
