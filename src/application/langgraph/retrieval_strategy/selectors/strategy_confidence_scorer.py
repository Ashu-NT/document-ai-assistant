from __future__ import annotations

from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy


def score_confidence(
    scores: dict[RetrievalStrategy, float],
    primary: RetrievalStrategy,
) -> float:
    best = scores.get(primary, 0.0)
    runner_up = max(
        (score for strategy, score in scores.items() if strategy != primary),
        default=0.0,
    )
    margin = best - runner_up
    if best >= 8.0 and margin >= 2.0:
        return 0.95
    if best >= 6.0:
        return 0.88
    if best >= 4.0:
        return 0.78
    return 0.65
