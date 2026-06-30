from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
    RetrievalStrategy,
)


@dataclass(slots=True)
class RetrievalPlanStep:
    step_id: str
    strategy: RetrievalStrategy
    query: str
    document_id: str | None
    top_k: int
    tool_name: str
    args: dict[str, Any] = field(default_factory=dict)
    output_key: str = ""
    required: bool = True
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "strategy": self.strategy.value,
            "query": self.query,
            "document_id": self.document_id,
            "top_k": self.top_k,
            "tool_name": self.tool_name,
            "args": dict(self.args),
            "output_key": self.output_key,
            "required": self.required,
            "reason": self.reason,
        }
