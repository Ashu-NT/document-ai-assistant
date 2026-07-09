from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import ContactPoint
from src.infrastructure.db.mappers import ContactPointMapper
from src.infrastructure.db.orm_models import ContactPointORM
from src.shared.exceptions import DatabaseError


class ContactPointReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_contact_points(
        self,
        document_id: str | None = None,
    ) -> list[ContactPoint]:
        try:
            statement = select(ContactPointORM)

            if document_id is not None:
                statement = statement.where(ContactPointORM.document_id == document_id)

            rows = self.session.execute(statement).scalars().all()
            return [ContactPointMapper.to_domain(row) for row in rows]
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list contact points.",
                details={"document_id": document_id},
            ) from exc

    def search_contact_points(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[ContactPoint]:
        try:
            like_pattern = f"%{query}%"
            statement = select(ContactPointORM).where(
                or_(
                    ContactPointORM.value.ilike(like_pattern),
                    ContactPointORM.label.ilike(like_pattern),
                    ContactPointORM.owner_name.ilike(like_pattern),
                )
            )

            if document_id is not None:
                statement = statement.where(ContactPointORM.document_id == document_id)

            rows = self.session.execute(statement).scalars().all()
            return [ContactPointMapper.to_domain(row) for row in rows]
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search contact points.",
                details={"query": query, "document_id": document_id},
            ) from exc
