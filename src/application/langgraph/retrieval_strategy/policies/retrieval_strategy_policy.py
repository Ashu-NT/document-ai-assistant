from dataclasses import dataclass

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)


@dataclass(slots=True)
class RetrievalStrategyPolicy:
    enabled: bool = True
    llm_strategy_enabled: bool = False
    max_strategies_per_query: int = 3
    default_strategy: RetrievalStrategy = RetrievalStrategy.GENERAL_HYBRID
    default_top_k: int = 5
    max_top_k: int = 15
    allow_multi_strategy: bool = True
    preserve_document_scope: bool = True
    fallback_to_hybrid: bool = True
    max_merged_chunks: int = 12
