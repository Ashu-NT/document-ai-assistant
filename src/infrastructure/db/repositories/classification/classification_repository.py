from sqlalchemy.orm import Session

from src.application.contracts.classification import ClassificationRepository
from src.domain.classification import ChunkClassification, DocumentClassification
from infrastructure.db.repositories.classification.chunk_classification_reader import (
    ChunkClassificationReader,
)
from src.infrastructure.db.repositories.classification.chunk_classification_writer import (
    ChunkClassificationWriter,
)
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
        self.chunk_reader = ChunkClassificationReader(session)
        self.chunk_writer = ChunkClassificationWriter(session)

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

    def save_chunk_classification(
        self,
        classification: ChunkClassification,
    ) -> None:
        self.chunk_writer.save(classification)

    def get_chunk_classification(
        self,
        chunk_id: str,
    ) -> ChunkClassification | None:
        return self.chunk_reader.get(chunk_id)