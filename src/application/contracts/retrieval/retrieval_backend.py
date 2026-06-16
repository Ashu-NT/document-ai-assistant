from typing import Protocol

from src.domain.retrieval import RetrievalQuery, RetrievalResult


class RetrievalBackend(Protocol):
    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        ...