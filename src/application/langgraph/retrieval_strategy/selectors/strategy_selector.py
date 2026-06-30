from __future__ import annotations

from typing import Protocol

from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategyDecision,
    RetrievalStrategySignal,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
)


class StrategySelector(Protocol):
    def select(
        self,
        *,
        context: RetrievalContext,
        signals: list[RetrievalStrategySignal],
        policy: RetrievalStrategyPolicy,
    ) -> RetrievalStrategyDecision: ...
