from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.shared.events.event_types import EventStatus
from src.shared.severity import Severity


@dataclass(slots=True)
class EventEnvelope:
    event_id: str
    event_type: str

    aggregate_type: str | None = None
    aggregate_id: str | None = None

    status: EventStatus = EventStatus.PENDING
    severity: Severity = Severity.INFO

    actor_id: str | None = None
    actor_type: str = "system"
    request_id: str | None = None
    correlation_id: str | None = None
    source: str | None = None

    payload: dict[str, Any] = field(default_factory=dict)

    occurred_at: datetime | None = None
    published_at: datetime | None = None