from dataclasses import dataclass
from enum import StrEnum

from src.application.services.answer_generation.intent.answer_intent_decision import (
    AnswerIntentDecision,
)
from src.application.services.answer_generation.intent.compound_question_detector import (
    CompoundQuestionDetector,
)


class DispatchBypassReason(StrEnum):
    """Explicit, enumerable reasons `DeterministicDispatchGate` can force a
    bypass to the full grounded LLM call instead of firing a deterministic
    renderer (PR 5, answering_flow_weakness_remediation_plan.md).
    `UNSUPPORTED_RENDERER`/`CONFLICTING_EVIDENCE`/`INCOMPLETE_EXHAUSTIVE_EVIDENCE`
    are added later (PR 8-10) once the evidence metadata they depend on
    exists -- this set is deliberately not exhaustive yet. A `StrEnum`
    (matching `AnswerIntent`/`RetrievalQueryIntent`'s own convention) so
    existing string comparisons/diagnostics serialization keep working
    unchanged."""

    CONTESTED_INTENT = "contested_intent"
    NO_SIGNAL = "no_signal"
    COMPOUND_QUESTION = "compound_question"


@dataclass(slots=True, frozen=True)
class DispatchGateDecision:
    should_bypass: bool
    reason: DispatchBypassReason | None = None
    margin: int | None = None
    compound_intent_value: str | None = None


class DeterministicDispatchGate:
    """Decides whether the deterministic-renderer bypass should even be
    attempted for this turn. Three independent reasons force a bypass to
    the full grounded LLM call instead:

    - The winning answer intent is contested (an exact scoring tie with its
      runner-up) -- firing a renderer chosen from a coin-flip classification
      risks confidently answering the wrong question (finding F2).
    - The winning answer intent has no real matched signal behind it at all
      (a pure fallback with an empty matched_signals list) -- same risk as
      a contested tie, from the opposite direction: nothing positively
      chose this intent, so a domain-specific renderer would be dispatched
      on the strength of a default, not a signal.
    - The question itself mixes two distinct intents via a coordinating
      conjunction or a multi-part question-mark boundary -- a single-purpose
      renderer can only ever answer one clause (finding F3). Previously
      handled by disclaiming the unanswered half after the fact; now
      handled by not taking that shortcut in the first place.

    See outputs/architecture/answering_and_prompt_fresh_audit.md.
    """

    def __init__(
        self,
        *,
        compound_question_detector: CompoundQuestionDetector | None = None,
    ) -> None:
        self._compound_question_detector = (
            compound_question_detector or CompoundQuestionDetector()
        )

    def evaluate(
        self,
        *,
        question: str,
        effective_intent,
        intent_decision: AnswerIntentDecision,
    ) -> DispatchGateDecision:
        # A caller can force `effective_intent` to something other than
        # what AnswerIntentAnalyzer.analyze() would have picked on its own
        # (e.g. an upstream decision already resolved a different way).
        # `intent_decision.is_contested`/`.matched_signals` describe the
        # analyzer's OWN winning candidate -- only meaningful when that
        # candidate actually matches what's driving this answer, otherwise
        # they describe a hypothetical intent that was never used.
        intent_decision_is_in_effect = intent_decision.intent == effective_intent
        if intent_decision_is_in_effect and intent_decision.is_contested:
            return DispatchGateDecision(
                should_bypass=True,
                reason=DispatchBypassReason.CONTESTED_INTENT,
                margin=intent_decision.margin,
            )
        if intent_decision_is_in_effect and not intent_decision.matched_signals:
            return DispatchGateDecision(
                should_bypass=True,
                reason=DispatchBypassReason.NO_SIGNAL,
            )
        compound_signal = self._compound_question_detector.detect(
            question=question,
            driving_intent=effective_intent,
        )
        if compound_signal.is_compound:
            return DispatchGateDecision(
                should_bypass=True,
                reason=DispatchBypassReason.COMPOUND_QUESTION,
                compound_intent_value=(
                    compound_signal.unrelated_intent.value
                    if compound_signal.unrelated_intent is not None
                    else None
                ),
            )
        return DispatchGateDecision(should_bypass=False)
