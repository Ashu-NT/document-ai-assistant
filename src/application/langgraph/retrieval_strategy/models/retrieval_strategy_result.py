from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.retrieval_strategy.models.retrieval_plan import (
    RetrievalPlan,
)
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy_decision import (
    RetrievalStrategyDecision,
)
from src.application.langgraph.retrieval_strategy.tracing import RetrievalStrategyTrace


@dataclass(slots=True)
class RetrievalStrategyResult:
    decision: RetrievalStrategyDecision
    plan: RetrievalPlan
    trace: RetrievalStrategyTrace
    diagnostics: dict[str, Any] = field(default_factory=dict)
