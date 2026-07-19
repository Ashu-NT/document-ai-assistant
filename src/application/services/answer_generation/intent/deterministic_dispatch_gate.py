from dataclasses import dataclass
from enum import StrEnum

from src.application.services.answer_generation.intent.answer_intent_decision import (
    AnswerIntentDecision,
)
from src.application.services.answer_generation.intent.compound_question_detector import (
    CompoundQuestionDetector,
)


class DispatchBypassReason(StrEnum):


    CONTESTED_INTENT = "contested_intent"
    NO_SIGNAL = "no_signal"
    COMPOUND_QUESTION = "compound_question"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    RETRIEVAL_CONTESTED = "retrieval_contested"


@dataclass(slots=True, frozen=True)
class DispatchGateDecision:
    should_bypass: bool
    reason: DispatchBypassReason | None = None
    margin: int | None = None
    compound_intent_value: str | None = None


class DeterministicDispatchGate:


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
        has_conflicting_evidence: bool = False,
        retrieval_intent_contested: bool = False,
    ) -> DispatchGateDecision:

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
        # W2, answering_flow_weakness_remediation_plan.md: the answer-side
        # decision above can look confident even when the *retrieval-side*
        # classification that actually selected this turn's evidence was
        # itself an exact tie -- a third, independent bypass condition, not
        # a merge of the two taxonomies.
        if retrieval_intent_contested:
            return DispatchGateDecision(
                should_bypass=True,
                reason=DispatchBypassReason.RETRIEVAL_CONTESTED,
            )
        if has_conflicting_evidence:
            return DispatchGateDecision(
                should_bypass=True,
                reason=DispatchBypassReason.CONFLICTING_EVIDENCE,
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
