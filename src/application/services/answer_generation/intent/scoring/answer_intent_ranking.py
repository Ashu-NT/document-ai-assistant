from __future__ import annotations

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.services.answer_generation.intent.scoring.answer_intent_vocabulary import (
    INTENT_PRIORITY,
)


def pick_intent(scores: dict[AnswerIntent, int]) -> AnswerIntent:
    best_score = max(scores.values())
    candidates = [
        intent for intent in INTENT_PRIORITY if scores.get(intent, 0) == best_score
    ]
    return candidates[0] if candidates else AnswerIntent.GENERAL


def runner_up(
    scores: dict[AnswerIntent, int],
    best_intent: AnswerIntent,
) -> tuple[AnswerIntent | None, int]:
    """Highest-scoring intent other than best_intent, tie-broken by the
    same INTENT_PRIORITY order pick_intent uses. None/0 when no other
    intent scored at all -- exposed on AnswerIntentDecision so callers
    get the same runner-up visibility RetrievalQueryIntentClassification
    already provides on the retrieval side, instead of compute_confidence()
    computing and discarding it internally."""
    runner_up_intent: AnswerIntent | None = None
    runner_up_score = 0
    for intent in INTENT_PRIORITY:
        if intent == best_intent:
            continue
        score = scores.get(intent, 0)
        if score > runner_up_score:
            runner_up_score = score
            runner_up_intent = intent
    if runner_up_score <= 0:
        return None, 0
    return runner_up_intent, runner_up_score
