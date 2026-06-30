from __future__ import annotations

from dataclasses import dataclass, field

from src.application.agent_runtime.react_loop.react_step import ReactStep


@dataclass(slots=True)
class ReactTrace:
    route: str | None
    steps: list[ReactStep] = field(default_factory=list)
    final_answer: str | None = None

    def is_empty(self) -> bool:
        return not self.steps
