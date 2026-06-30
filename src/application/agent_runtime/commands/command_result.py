from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CommandResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    should_exit: bool = False
    update_session: bool = False
    render_as: str = "message"
