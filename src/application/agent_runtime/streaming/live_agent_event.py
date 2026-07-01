from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LiveAgentEventType(str, Enum):
    RUN_STARTED = "run_started"
    UNDERSTAND_REQUEST = "understand_request"
    STRATEGY_STARTED = "strategy_started"
    STRATEGY_COMPLETED = "strategy_completed"
    PLAN_STARTED = "plan_started"
    PLAN_COMPLETED = "plan_completed"
    ACTION_STARTED = "action_started"
    ACTION_COMPLETED = "action_completed"
    OBSERVATION = "observation"
    REFLECTION_STARTED = "reflection_started"
    REFLECTION_COMPLETED = "reflection_completed"
    FINAL_STARTED = "final_started"
    FINAL_COMPLETED = "final_completed"
    RUN_COMPLETED = "run_completed"
    ERROR = "error"
    BLOCKED = "blocked"


@dataclass(slots=True)
class LiveAgentEvent:
    event_type: LiveAgentEventType
    payload: dict[str, Any] = field(default_factory=dict)
