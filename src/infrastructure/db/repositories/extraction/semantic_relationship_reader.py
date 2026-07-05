from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import SemanticRelationship
from src.infrastructure.db.mappers import SemanticRelationshipMapper
from src.infrastructure.db.orm_models import SemanticRelationshipORM
from src.shared.exceptions import DatabaseError


class SemanticRelationshipReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_semantic_relationships(
        self,
        document_id: str | None = None,
    ) -> list[SemanticRelationship]:
        try:
            statement = select(SemanticRelationshipORM)

            if document_id is not None:
                statement = statement.where(
                    SemanticRelationshipORM.document_id == document_id
                )

            rows = self.session.execute(statement).scalars().all()

            return [SemanticRelationshipMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list semantic relationships.",
                details={"document_id": document_id},
            ) from exc
