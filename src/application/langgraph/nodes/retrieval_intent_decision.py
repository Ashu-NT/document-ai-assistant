from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalIntentDecision:
    """The full persisted retrieval-side intent classification (PR 1's
    RetrievalQuery.intent_* fields), extracted once from the serialized
    QuestionAnsweringResult payload for any node/service that needs more
    than the bare intent value -- see PR 2/3,
    answering_flow_weakness_remediation_plan.md. Mirrors
    AnswerIntentDecision's best_score/runner_up_score/is_contested naming
    for the same concept on the answer-generation side, so a reader who
    knows one recognizes the other."""

    intent: str
    best_score: int | None = None
    runner_up_intent: str | None = None
    runner_up_score: int | None = None
    gap: int | None = None
    confidence: float | None = None

    @property
    def is_contested(self) -> bool:
        return self.runner_up_intent is not None and self.gap == 0
