from __future__ import annotations

from typing import Protocol

from src.application.langgraph.reflection.models import RetryPlan
from src.application.langgraph.reflection.strategies.retry_reformulation.retry_reformulation_context import (
    RetryReformulationContext,
)


class RetryReformulationStrategy(Protocol):
    """Produces a `RetryPlan` (reformulated query text + a recommended
    retrieval strategy hint) for one `RetrievalQueryIntent` category, or,
    for the generic default, for any category with no registered
    specialization. Unifies what were previously two independent
    keyword-driven decisions (`RetryQueryBuilder`'s query text,
    `StrategyRetryPolicy`'s strategy recommendation) behind one dispatch
    point."""

    def build_retry_plan(self, context: RetryReformulationContext) -> RetryPlan: ...
