from __future__ import annotations

from dataclasses import dataclass

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


@dataclass(slots=True, frozen=True)
class AnswerIntentDecision:
    intent: AnswerIntent
    confidence: float
    reason: str
    matched_signals: list[str]
    runner_up_intent: AnswerIntent | None = None
    runner_up_score: int = 0
    best_score: int = 0

    @property
    def margin(self) -> int | None:
        """`best_score - runner_up_score`, or `None` when no runner-up
        scored at all (nothing to be contested against). Unlike
        `confidence` -- a coarse bucketed float that only actually reacts
        to the margin in its top two tiers (see `compute_confidence()`) --
        this is the real, fine-grained "how contested was this
        classification" signal, mirroring `RetrievalQueryIntentClassification
        .gap` on the retrieval side."""
        if self.runner_up_intent is None:
            return None
        return self.best_score - self.runner_up_score

    @property
    def is_contested(self) -> bool:
        """True on an exact scoring tie between the winning intent and its
        runner-up (margin == 0) -- the same "genuine tie, not a fuzzy
        threshold guess" precedent as the retrieval-side ambiguity
        detector. Deliberately narrow for now: widen only after collecting
        real margin telemetry (see the `answer_intent_resolved` log line in
        `AnswerIntentAnalyzer.analyze()`), not by guessing a wider band
        upfront."""
        return self.margin is not None and self.margin <= 0


def compute_confidence(*, best_score: int, runner_up_score: int) -> float:
    margin = best_score - runner_up_score
    if best_score >= 10 and margin >= 3:
        return 0.95
    if best_score >= 8 and margin >= 2:
        return 0.9
    if best_score >= 6:
        return 0.82
    if best_score >= 4:
        return 0.72
    return 0.62
