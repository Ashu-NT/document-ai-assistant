from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ActionResult:
    entity_type: str | None = None
    entity_id: str | None = None
    message: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)