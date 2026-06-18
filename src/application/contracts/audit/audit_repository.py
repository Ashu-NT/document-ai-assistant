from typing import Protocol

from src.domain.audit import AuditRecord


class AuditRepository(Protocol):
    def save(self, audit: AuditRecord) -> None:
        ...

    def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50,
    ) -> list[AuditRecord]:
        ...