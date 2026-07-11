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
