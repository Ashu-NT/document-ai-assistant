from src.application.contracts.retrieval import Reranker
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class NoOpReranker(Reranker):
    def rerank(
        self,
        query: RetrievalQuery,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        return chunks