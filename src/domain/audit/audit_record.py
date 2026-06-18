from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.shared.audit.audit_types import AuditOutcome, AuditSeverity


@dataclass
class AuditRecord:
    audit_id: str = field(default_factory=lambda: str(uuid4()))

    action: str = ""
    outcome: AuditOutcome = AuditOutcome.SUCCESS
    severity: AuditSeverity = AuditSeverity.LOW

    entity_type: str | None = None
    entity_id: str | None = None

    actor_id: str | None = None
    actor_type: str = "system"

    request_id: str | None = None
    correlation_id: str | None = None
    source: str | None = None
    ip_address: str | None = None

    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))