from typing import Protocol

from src.domain.workflow import WorkflowState


class CheckpointStore(Protocol):
    def save(self, state: WorkflowState) -> None:
        ...

    def load(self, workflow_id: str) -> WorkflowState | None:
        ...