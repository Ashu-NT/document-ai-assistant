from typing import Protocol

from src.domain.workflow import WorkflowResult, WorkflowState


class WorkflowRunner(Protocol):
    def run(self, state: WorkflowState) -> WorkflowResult:
        ...