from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ClarificationPlan:
    question: str
    options: list[str] = field(default_factory=list)
    original_user_input: str = ""
    reason: str = ""
    resume_route: str | None = None
    resume_payload: dict[str, Any] = field(default_factory=dict)
