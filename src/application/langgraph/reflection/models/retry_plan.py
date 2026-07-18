from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.langgraph.retrieval_strategy import RetrievalStrategy


@dataclass(slots=True)
class RetryPlan:
    retry_query: str
    document_id: str | None
    top_k: int | None
    reason: str
    preserve_initial_evidence: bool = True
    # Populated by RetryReformulationStrategyRegistry so a single decision
    # carries both the reformulated query text and a recommended retrieval
    # strategy -- previously two uncoordinated keyword scanners in separate
    # packages (RetryQueryBuilder here, StrategyRetryPolicy in
    # retrieval_strategy) produced these independently.
    retrieval_strategy_hint: "RetrievalStrategy | None" = None
    secondary_strategy_hints: "list[RetrievalStrategy]" = field(default_factory=list)
