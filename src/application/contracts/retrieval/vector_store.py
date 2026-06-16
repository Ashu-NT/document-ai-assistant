from typing import Protocol

from src.domain.document.entities import DocumentChunk
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class VectorStore(Protocol):
    def save_chunk_vectors(self, chunks: list[DocumentChunk]) -> None:
        ...

    def search(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        ...

    def delete_document_vectors(self, document_id: str) -> None:
        ...