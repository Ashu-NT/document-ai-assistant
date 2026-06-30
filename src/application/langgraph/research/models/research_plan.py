from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.application.langgraph.research.models.research_goal import ResearchGoal
from src.application.langgraph.research.models.research_task import ResearchTask


@dataclass(slots=True)
class ResearchPlan:
    plan_id: str
    goal: ResearchGoal
    tasks: list[ResearchTask]
    reason: str
    source: str
    requires_document: bool
    max_iterations: int
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def task_count(self) -> int:
        return len(self.tasks)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
