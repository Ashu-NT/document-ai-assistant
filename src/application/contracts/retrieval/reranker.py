from typing import Protocol

from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class Reranker(Protocol):
    def rerank(
        self,
        query: RetrievalQuery,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        ...