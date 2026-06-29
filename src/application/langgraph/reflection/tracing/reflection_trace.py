from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ReflectionTrace:
    decision: str
    confidence: float
    overall_score: float
    reason: str
    diagnostics: dict[str, Any] = field(default_factory=dict)
