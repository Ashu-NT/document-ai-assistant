from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.classification import DocumentClassification
from src.infrastructure.db.mappers.classification import (
    DocumentClassificationMapper,
)
from shared.exceptions import DatabaseError


class DocumentClassificationWriter:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, classification: DocumentClassification) -> None:
        try:
            self.session.merge(
                DocumentClassificationMapper.to_orm(classification)
            )
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save document classification.",
                details={"document_id": classification.document_id},
            ) from exc