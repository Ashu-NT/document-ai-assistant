from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.domain.common import AuditMetadata


@dataclass(slots=True)
class DomainEvent:
    event_id: str
    event_type: str

    aggregate_id: str | None = None
    aggregate_type: str | None = None

    payload: dict[str, Any] = field(default_factory=dict)

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    @property
    def occurred_at(self) -> datetime:
        return self.audit.created_at