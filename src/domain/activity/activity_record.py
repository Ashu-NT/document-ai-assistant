from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.domain.activity.activity_types import ActivitySeverity, ActivityStatus


@dataclass
class ActivityRecord:
    activity_id: str = field(default_factory=lambda: str(uuid4()))

    action: str = ""
    message: str = ""

    entity_type: str | None = None
    entity_id: str | None = None

    status: ActivityStatus = ActivityStatus.COMPLETED
    severity: ActivitySeverity = ActivitySeverity.INFO

    actor_id: str | None = None
    actor_type: str = "system"

    request_id: str | None = None
    correlation_id: str | None = None
    source: str | None = None

    payload: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))