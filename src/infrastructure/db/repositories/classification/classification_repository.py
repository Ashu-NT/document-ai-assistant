from sqlalchemy.orm import Session

from src.application.contracts.classification import ClassificationRepository
from src.domain.classification import DocumentClassification
from src.infrastructure.db.repositories.classification.document_classification_reader import (
    DocumentClassificationReader,
)
from src.infrastructure.db.repositories.classification.document_classification_writer import (
    DocumentClassificationWriter,
)


class SqlAlchemyClassificationRepository(ClassificationRepository):
    def __init__(self, session: Session) -> None:
        self.document_reader = DocumentClassificationReader(session)
        self.document_writer = DocumentClassificationWriter(session)

    def save_document_classification(
        self,
        classification: DocumentClassification,
    ) -> None:
        self.document_writer.save(classification)

    def get_document_classification(
        self,
        document_id: str,
    ) -> DocumentClassification | None:
        return self.document_reader.get(document_id)

    def delete_document_classification(self, document_id: str) -> None:
        self.document_writer.delete_by_document(document_id)