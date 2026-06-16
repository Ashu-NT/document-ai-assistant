from typing import Protocol

from src.domain.classification import DocumentClassification
from src.domain.document import DocumentGraph


class DocumentClassifier(Protocol):
    def classify_document(self, document_graph: DocumentGraph) -> DocumentClassification:
        ...