from typing import Protocol

from src.domain.workflows import WorkflowResult, WorkflowState


class WorkflowRunner(Protocol):
    def run(self, state: WorkflowState) -> WorkflowResult:
        ...