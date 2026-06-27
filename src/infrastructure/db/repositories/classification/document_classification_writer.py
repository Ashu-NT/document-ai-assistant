from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.classification import DocumentClassification
from src.infrastructure.db.mappers import (
    DocumentClassificationMapper,
)
from src.infrastructure.db.orm_models import DocumentClassificationORM
from src.shared.exceptions import DatabaseError


class DocumentClassificationWriter:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, classification: DocumentClassification) -> None:
        try:
            self.session.execute(
                delete(DocumentClassificationORM).where(
                    DocumentClassificationORM.document_id == classification.document_id
                )
            )
            self.session.merge(
                DocumentClassificationMapper.to_orm(classification)
            )
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save document classification.",
                details={"document_id": classification.document_id},
            ) from exc
