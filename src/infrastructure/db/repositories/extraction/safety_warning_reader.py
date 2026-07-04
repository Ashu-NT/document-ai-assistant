from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import SafetyWarning
from src.infrastructure.db.mappers import SafetyWarningMapper
from src.infrastructure.db.orm_models import SafetyWarningORM
from src.shared.exceptions import DatabaseError


class SafetyWarningReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_safety_warnings(
        self,
        document_id: str | None = None,
    ) -> list[SafetyWarning]:
        try:
            statement = select(SafetyWarningORM)

            if document_id is not None:
                statement = statement.where(
                    SafetyWarningORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [SafetyWarningMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list safety warnings.",
                details={"document_id": document_id},
            ) from exc

    def search_safety_warnings(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[SafetyWarning]:
        try:
            pattern = f"%{query}%"
            statement = select(SafetyWarningORM).where(
                or_(
                    SafetyWarningORM.message.ilike(pattern),
                    SafetyWarningORM.component_name.ilike(pattern),
                    SafetyWarningORM.warning_type.ilike(pattern),
                )
            )

            if document_id is not None:
                statement = statement.where(
                    SafetyWarningORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [SafetyWarningMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search safety warnings.",
                details={"query": query, "document_id": document_id},
            ) from exc
