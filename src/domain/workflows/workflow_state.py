from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkflowState:
    workflow_id: str
    workflow_name: str

    current_step: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    failed_step: str | None = None

    data: dict[str, Any] = field(default_factory=dict)

    def mark_step_started(self, step_name: str) -> None:
        self.current_step = step_name

    def mark_step_completed(self, step_name: str) -> None:
        if step_name not in self.completed_steps:
            self.completed_steps.append(step_name)

        if self.current_step == step_name:
            self.current_step = None

    def mark_step_failed(self, step_name: str) -> None:
        self.failed_step = step_name
        self.current_step = None

    def has_failed(self) -> bool:
        return self.failed_step is not None