from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.classification import DocumentClassification
from src.infrastructure.db.mappers import (
    DocumentClassificationMapper,
)
from src.infrastructure.db.orm_models import DocumentClassificationORM
from src.shared.exceptions import DatabaseError


class DocumentClassificationReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, document_id: str) -> DocumentClassification | None:
        try:
            statement = select(DocumentClassificationORM).where(
                DocumentClassificationORM.document_id == document_id,
            )

            row = self.session.execute(statement).scalar_one_or_none()

            if row is None:
                return None

            return DocumentClassificationMapper.to_domain(row)

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load document classification.",
                details={"document_id": document_id},
            ) from exc