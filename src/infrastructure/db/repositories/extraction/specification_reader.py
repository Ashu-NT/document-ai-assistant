from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import Specification
from src.infrastructure.db.mappers import SpecificationMapper
from src.infrastructure.db.orm_models import SpecificationORM
from src.shared.exceptions import DatabaseError


class SpecificationReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_specifications(
        self,
        document_id: str | None = None,
    ) -> list[Specification]:
        try:
            statement = select(SpecificationORM)

            if document_id is not None:
                statement = statement.where(
                    SpecificationORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [SpecificationMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list specifications.",
                details={"document_id": document_id},
            ) from exc

    def search_specifications(
        self,
        query: str,
        document_id: str | None = None,
    ) -> list[Specification]:
        try:
            pattern = f"%{query}%"
            statement = select(SpecificationORM).where(
                or_(
                    SpecificationORM.parameter.ilike(pattern),
                    SpecificationORM.value.ilike(pattern),
                    SpecificationORM.component_name.ilike(pattern),
                )
            )

            if document_id is not None:
                statement = statement.where(
                    SpecificationORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [SpecificationMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search specifications.",
                details={"query": query, "document_id": document_id},
            ) from exc
