from typing import Protocol

from src.domain.classification import DocumentClassification


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

    def delete_document_classification(self, document_id: str) -> None:
        ...