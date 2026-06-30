from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.agent_runtime.react_loop.react_event import ReactEvent


@dataclass(slots=True)
class ReactStep:
    index: int
    event_type: ReactEvent
    title: str
    body: str
    metadata: dict[str, Any] = field(default_factory=dict)
