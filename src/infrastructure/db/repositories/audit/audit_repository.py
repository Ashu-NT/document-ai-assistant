from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.application.contracts.audit import AuditRepository
from src.domain.audit import AuditRecord
from src.infrastructure.db.mappers import AuditRecordMapper
from src.infrastructure.db.orm_models import AuditRecordORM
from src.shared.exceptions import DatabaseError


class SqlAlchemyAuditRepository(AuditRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, audit: AuditRecord) -> None:
        try:
            self.session.add(AuditRecordMapper.to_orm(audit))
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save audit record.",
                details={
                    "audit_id": audit.audit_id,
                    "action": audit.action,
                    "entity_type": audit.entity_type,
                    "entity_id": audit.entity_id,
                },
            ) from exc

    def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50,
    ) -> list[AuditRecord]:
        try:
            statement = (
                select(AuditRecordORM)
                .where(AuditRecordORM.entity_type == entity_type)
                .where(AuditRecordORM.entity_id == entity_id)
                .order_by(desc(AuditRecordORM.created_at))
                .limit(limit)
            )

            rows = self.session.execute(statement).scalars().all()

            return [AuditRecordMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list audit records by entity.",
                details={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "limit": limit,
                },
            ) from exc