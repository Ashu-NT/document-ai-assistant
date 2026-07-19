from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.application.langgraph.reflection.models import ReflectionDecision

if TYPE_CHECKING:
    from src.application.langgraph.retrieval_strategy import RetrievalStrategy


@dataclass(slots=True, frozen=True)
class RetryReformulationContext:
    """Everything a `RetryReformulationStrategy` needs to produce a
    `RetryPlan` -- bundled for the same reason as
    `EvidenceSufficiencyContext`: keeps the strategy interface from growing
    a long parameter list as more strategies are added."""

    original_user_question: str
    answer_intent: str | None
    selected_document_id: str | None
    reflection_decision: ReflectionDecision
    top_k: int | None
    current_primary_strategy: "RetrievalStrategy | None" = None
