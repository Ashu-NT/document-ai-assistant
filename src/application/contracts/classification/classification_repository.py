from typing import Protocol

from src.domain.classification import ChunkClassification, DocumentClassification


class ClassificationRepository(Protocol):
    def save_document_classification(
        self,
        classification: DocumentClassification,
    ) -> None:
        ...

    def get_document_classification(
        self,
        document_id: str,
    ) -> DocumentClassification | None:
        ...

    def save_chunk_classification(
        self,
        classification: ChunkClassification,
    ) -> None:
        ...

    def get_chunk_classification(
        self,
        chunk_id: str,
    ) -> ChunkClassification | None:
        ...

    def list_chunk_classifications(
        self,
        document_id: str,
    ) -> list[ChunkClassification]:
        ...