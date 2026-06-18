from dataclasses import dataclass


@dataclass(frozen=True)
class AuditContext:
    actor_id: str | None = None
    actor_type: str = "system"
    request_id: str | None = None
    correlation_id: str | None = None
    source: str | None = None
    ip_address: str | None = None