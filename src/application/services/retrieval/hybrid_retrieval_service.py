from src.application.contracts.retrieval import (
    KeywordIndex,
    RetrievalBackend,
    Reranker,
    VectorStore,
)
from src.application.validation.retrieval import RetrievalQueryValidator
from src.domain.retrieval import RetrievalQuery, RetrievalResult, RetrievedChunk
from src.shared.ids import IdGenerator


class HybridRetrievalService(RetrievalBackend):
    def __init__(
        self,
        *,
        keyword_index: KeywordIndex,
        id_generator: IdGenerator,
        retrieval_query_validator: RetrievalQueryValidator,
        vector_store: VectorStore | None = None,
        reranker: Reranker | None = None,
    ) -> None:
        self.keyword_index = keyword_index
        self.id_generator = id_generator
        self.retrieval_query_validator = retrieval_query_validator
        self.vector_store = vector_store
        self.reranker = reranker

    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        validation = self.retrieval_query_validator.validate(query)
        validation.raise_if_invalid()

        results: list[RetrievedChunk] = []

        results.extend(self.keyword_index.search(query))

        if self.vector_store is not None:
            results.extend(self.vector_store.search(query))

        deduplicated = self._deduplicate(results)

        ranked = (
            self.reranker.rerank(query, deduplicated)
            if self.reranker is not None
            else deduplicated
        )

        final_chunks = ranked[: query.top_k]

        return RetrievalResult(
            result_id=self.id_generator.new_retrieval_id(),
            query=query,
            chunks=final_chunks,
            used_dense=self.vector_store is not None,
            used_keyword=True,
            used_sql=True,
            total_candidates=len(deduplicated),
        )

    def _deduplicate(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        seen: set[str] = set()
        unique: list[RetrievedChunk] = []

        for chunk in chunks:
            if chunk.chunk_id in seen:
                continue

            seen.add(chunk.chunk_id)
            unique.append(chunk)

        return unique
