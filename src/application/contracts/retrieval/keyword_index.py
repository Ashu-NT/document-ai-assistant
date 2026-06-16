from typing import Protocol

from src.domain.document.entities import DocumentChunk
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class KeywordIndex(Protocol):
    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        ...

    def search(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        ...