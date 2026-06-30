from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy_signal import (
    RetrievalStrategySignal,
)


@dataclass(slots=True)
class RetrievalStrategyDecision:
    primary_strategy: RetrievalStrategy
    secondary_strategies: list[RetrievalStrategy] = field(default_factory=list)
    confidence: float = 0.0
    reason: str = ""
    signals: list[RetrievalStrategySignal] = field(default_factory=list)
    requires_document: bool = False
    document_id: str | None = None
    query: str = ""
    rewritten_query: str | None = None
    top_k: int = 5
    use_llm_selector: bool = False
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def selected_strategies(self) -> list[RetrievalStrategy]:
        if self.primary_strategy == RetrievalStrategy.MULTI_STRATEGY:
            return list(self.secondary_strategies)
        return [self.primary_strategy, *self.secondary_strategies]
