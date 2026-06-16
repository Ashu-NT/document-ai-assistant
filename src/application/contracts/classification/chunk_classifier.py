from typing import Protocol

from src.domain.classification import ChunkClassification
from src.domain.document.entities import DocumentChunk


class ChunkClassifier(Protocol):
    def classify_chunk(self, chunk: DocumentChunk) -> ChunkClassification:
        ...