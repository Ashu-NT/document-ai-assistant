from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkflowResult:
    workflow_id: str
    workflow_name: str

    success: bool

    message: str | None = None
    error_message: str | None = None

    data: dict[str, Any] = field(default_factory=dict)

    def failed(self) -> bool:
        return not self.success