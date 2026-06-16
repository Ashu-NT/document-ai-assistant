from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class AuditMetadata:
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime | None = None
    created_by: str = "system"
