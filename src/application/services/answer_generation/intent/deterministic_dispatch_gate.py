from dataclasses import dataclass

from src.application.services.answer_generation.intent.answer_intent_decision import (
    AnswerIntentDecision,
)
from src.application.services.answer_generation.intent.compound_question_detector import (
    CompoundQuestionDetector,
)


@dataclass(slots=True, frozen=True)
class DispatchGateDecision:
    should_bypass: bool
    reason: str | None = None
    margin: int | None = None
    compound_intent_value: str | None = None


class DeterministicDispatchGate:
    """Decides whether the deterministic-renderer bypass should even be
    attempted for this turn. Two independent reasons force a bypass to the
    full grounded LLM call instead:

    - The winning answer intent is contested (an exact scoring tie with its
      runner-up) -- firing a renderer chosen from a coin-flip classification
      risks confidently answering the wrong question (finding F2).
    - The question itself mixes two distinct intents via a coordinating
      conjunction -- a single-purpose renderer can only ever answer one half
      (finding F3). Previously handled by disclaiming the unanswered half
      after the fact; now handled by not taking that shortcut in the first
      place.

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
        # `intent_decision.is_contested` describes a tie among the
        # analyzer's OWN candidates -- only meaningful when its winning
        # intent actually matches what's driving this answer, otherwise
        # it's a tie about a hypothetical intent that was never used.
        if intent_decision.intent == effective_intent and intent_decision.is_contested:
            return DispatchGateDecision(
                should_bypass=True,
                reason="contested_intent",
                margin=intent_decision.margin,
            )
        compound_intent = self._compound_question_detector.detect(
            question=question,
            driving_intent=effective_intent,
        )
        if compound_intent is not None:
            return DispatchGateDecision(
                should_bypass=True,
                reason="compound_question",
                compound_intent_value=compound_intent.value,
            )
        return DispatchGateDecision(should_bypass=False)
