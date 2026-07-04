from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import TroubleshootingEntry
from src.infrastructure.db.mappers import TroubleshootingEntryMapper
from src.infrastructure.db.orm_models import TroubleshootingEntryORM
from src.shared.exceptions import DatabaseError


class TroubleshootingEntryReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_troubleshooting_entries(
        self,
        document_id: str | None = None,
    ) -> list[TroubleshootingEntry]:
        try:
            statement = select(TroubleshootingEntryORM)

            if document_id is not None:
                statement = statement.where(
                    TroubleshootingEntryORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [TroubleshootingEntryMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list troubleshooting entries.",
                details={"document_id": document_id},
            ) from exc

    def list_by_equipment_id(
        self,
        equipment_id: str,
    ) -> list[TroubleshootingEntry]:
        try:
            statement = select(TroubleshootingEntryORM).where(
                TroubleshootingEntryORM.equipment_id == equipment_id
            )

            rows = self.session.execute(statement).scalars().all()

            return [TroubleshootingEntryMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list troubleshooting entries for equipment.",
                details={"equipment_id": equipment_id},
            ) from exc

    def search_troubleshooting_entries(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[TroubleshootingEntry]:
        try:
            pattern = f"%{query}%"
            statement = select(TroubleshootingEntryORM).where(
                or_(
                    TroubleshootingEntryORM.symptom.ilike(pattern),
                    TroubleshootingEntryORM.cause.ilike(pattern),
                    TroubleshootingEntryORM.remedy.ilike(pattern),
                    TroubleshootingEntryORM.component_name.ilike(pattern),
                )
            )

            if document_id is not None:
                statement = statement.where(
                    TroubleshootingEntryORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [TroubleshootingEntryMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search troubleshooting entries.",
                details={"query": query, "document_id": document_id},
            ) from exc
