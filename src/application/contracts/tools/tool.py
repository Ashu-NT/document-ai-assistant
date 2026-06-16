from typing import Protocol, Any

from pydantic import BaseModel


class ToolInput(BaseModel):
    pass


class ToolOutput(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None


class Tool(Protocol):
    name: str
    description: str

    def execute(self, input_data: ToolInput) -> ToolOutput:
        ...