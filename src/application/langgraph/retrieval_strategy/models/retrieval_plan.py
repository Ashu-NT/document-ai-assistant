from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.retrieval_strategy.models.retrieval_plan_step import (
    RetrievalPlanStep,
)
from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)


@dataclass(slots=True)
class RetrievalPlan:
    plan_id: str
    original_query: str
    document_id: str | None
    steps: list[RetrievalPlanStep] = field(default_factory=list)
    primary_strategy: RetrievalStrategy = RetrievalStrategy.GENERAL_HYBRID
    reason: str = ""
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "original_query": self.original_query,
            "document_id": self.document_id,
            "steps": [step.to_dict() for step in self.steps],
            "primary_strategy": self.primary_strategy.value,
            "reason": self.reason,
            "diagnostics": dict(self.diagnostics),
        }
