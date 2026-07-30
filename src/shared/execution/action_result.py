from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ActionResult:
    entity_type: str | None = None
    entity_id: str | None = None
    message: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    before_state: dict[str, Any] | None = None
    event_id: str = field(default_factory=lambda: str(uuid4()))