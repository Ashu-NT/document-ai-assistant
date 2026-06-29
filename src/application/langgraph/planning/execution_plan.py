from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.planning.plan_step import PlanStep


@dataclass(slots=True, frozen=True)
class ExecutionPlan:
    plan_id: str
    goal: str
    steps: list[PlanStep]
    reason: str
    requires_document: bool = False
    document_id: str | None = None
    document_title: str | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not self.steps

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def tool_names(self) -> list[str]:
        return [step.tool_name for step in self.steps]

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "steps": [step.to_dict() for step in self.steps],
            "reason": self.reason,
            "requires_document": self.requires_document,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "diagnostics": dict(self.diagnostics),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ExecutionPlan":
        return cls(
            plan_id=str(value["plan_id"]),
            goal=str(value["goal"]),
            steps=[
                PlanStep.from_dict(item)
                for item in list(value.get("steps", []))
                if isinstance(item, dict)
            ],
            reason=str(value["reason"]),
            requires_document=bool(value.get("requires_document", False)),
            document_id=value.get("document_id"),
            document_title=value.get("document_title"),
            diagnostics=dict(value.get("diagnostics", {})),
        )
