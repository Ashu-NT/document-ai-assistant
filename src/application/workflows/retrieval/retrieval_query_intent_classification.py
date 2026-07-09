from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Mapping

from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)

ResolutionTier = Literal[
    "scored",
    "chunk_type_fallback",
    "identifier_fallback",
    "comparative_fallback",
    "fuzzy_fallback",
    "general",
]


@dataclass(frozen=True, slots=True)
class RetrievalQueryIntentClassification:
    """Rich result of classifying a query's retrieval intent.

    `RetrievalQueryIntentInferer.infer()` still returns a bare
    `RetrievalQueryIntent` for backward compatibility with existing callers;
    this type is what `classify()` returns for consumers that need the
    score/confidence signal behind the winning intent -- most notably a
    future LLM-clarification trigger, which should only fire when
    `confidence` is low rather than on every query.
    """

    intent: RetrievalQueryIntent
    score: int
    runner_up_intent: RetrievalQueryIntent | None
    runner_up_score: int
    scores: Mapping[RetrievalQueryIntent, int] = field(default_factory=dict)
    resolution_tier: ResolutionTier = "general"
    fallback_reason: str | None = None
    is_comparative: bool = False

    @property
    def gap(self) -> int:
        return self.score - self.runner_up_score

    @property
    def confidence(self) -> float:
        """Bounded [0, 1] heuristic blending absolute score strength with
        separation from the runner-up. Sketch only: the eventual
        LLM-clarification trigger owns the final formula/threshold; this
        exists so that consumer can be built without changing this type."""
        if self.resolution_tier == "scored":
            strength = min(self.score / 8.0, 1.0)
            separation = (
                1.0 if self.runner_up_intent is None else min(self.gap / 4.0, 1.0)
            )
            return round(0.5 * strength + 0.5 * separation, 3)
        if self.resolution_tier in ("comparative_fallback", "fuzzy_fallback"):
            # Weaker signal than chunk_type_fallback/identifier_fallback: no
            # topic marker matched at all, only a shape heuristic (comparison
            # phrasing) or a near-miss on a marker's exact spelling.
            return 0.3
        return 0.5

    def top_intents_within(self, margin: int) -> tuple[RetrievalQueryIntent, ...]:
        """Every candidate intent whose score is within `margin` of the
        winner's score -- for a future near-tie/clarification consumer."""
        return tuple(
            intent
            for intent, score in self.scores.items()
            if self.score - score <= margin
        )

    def __str__(self) -> str:
        return str(self.intent)
