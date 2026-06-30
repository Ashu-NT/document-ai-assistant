from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.retrieval_strategy.models.retrieval_plan import (
    RetrievalPlan,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


@dataclass(slots=True)
class RetrievalExecutionResult:
    plan: RetrievalPlan
    success: bool
    step_results: dict[str, Any] = field(default_factory=dict)
    evidence_chunks: list[RetrievedChunk] = field(default_factory=list)
    context_document_ids: list[str] = field(default_factory=list)
    tool_names: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan": self.plan.to_dict(),
            "success": self.success,
            "step_results": dict(self.step_results),
            "evidence_chunks": list(self.evidence_chunks),
            "context_document_ids": list(self.context_document_ids),
            "tool_names": list(self.tool_names),
            "errors": list(self.errors),
            "diagnostics": dict(self.diagnostics),
        }
