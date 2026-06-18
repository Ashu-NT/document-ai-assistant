from src.application.contracts.retrieval import KeywordIndex
from src.domain.document.entities import DocumentChunk
from src.domain.retrieval import RetrievalQuery, RetrievedChunk
from src.infrastructure.db.repositories.retrieval import SqlKeywordRepository


class SqlKeywordIndex(KeywordIndex):
    def __init__(self, repository: SqlKeywordRepository) -> None:
        self.repository = repository

    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        # Chunks are already persisted in SQLite.
        return None

    def search(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        return self.repository.search_chunks(
            query=query.query_text,
            limit=query.top_k,
        )