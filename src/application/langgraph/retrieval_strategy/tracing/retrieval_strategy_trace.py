from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RetrievalStrategyTrace:
    signals: list[dict[str, Any]] = field(default_factory=list)
    deterministic_decision: dict[str, Any] | None = None
    llm_decision: dict[str, Any] | None = None
    final_decision: dict[str, Any] | None = None
    fallback_reason: str | None = None
    plan_steps: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
