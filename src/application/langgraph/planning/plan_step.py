from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class PlanStep:
    step_id: str
    tool_name: str
    description: str
    input_key: str | None = None
    output_key: str = ""
    args: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "tool_name": self.tool_name,
            "description": self.description,
            "input_key": self.input_key,
            "output_key": self.output_key,
            "args": dict(self.args),
            "depends_on": list(self.depends_on),
            "required": self.required,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PlanStep":
        return cls(
            step_id=str(value["step_id"]),
            tool_name=str(value["tool_name"]),
            description=str(value["description"]),
            input_key=value.get("input_key"),
            output_key=str(value["output_key"]),
            args=dict(value.get("args", {})),
            depends_on=list(value.get("depends_on", [])),
            required=bool(value.get("required", True)),
        )
