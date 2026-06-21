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
        rrf_constant: int = 60,
    ) -> None:
        self.keyword_index = keyword_index
        self.id_generator = id_generator
        self.retrieval_query_validator = retrieval_query_validator
        self.vector_store = vector_store
        self.reranker = reranker
        self.rrf_constant = rrf_constant

    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        validation = self.retrieval_query_validator.validate(query)
        validation.raise_if_invalid()

        source_results = self._collect_source_results(query)
        fused_candidates = self._fuse_results(source_results)
        ranked = (
            self.reranker.rerank(
                query,
                self._prepare_for_reranking(fused_candidates),
            )
            if self.reranker is not None
            else fused_candidates
        )
        final_chunks = ranked[: query.top_k]

        return RetrievalResult(
            result_id=self.id_generator.new_retrieval_id(),
            query=query,
            chunks=final_chunks,
            used_dense=bool(query.use_dense and self.vector_store is not None),
            used_keyword=bool(query.use_keyword),
            used_sql=bool(query.use_sql),
            total_candidates=len(fused_candidates),
        )

    def _collect_source_results(
        self,
        query: RetrievalQuery,
    ) -> list[tuple[str, list[RetrievedChunk]]]:
        source_results: list[tuple[str, list[RetrievedChunk]]] = []

        if query.use_keyword or query.use_sql:
            source_results.append(
                ("sql_keyword", self.keyword_index.search(query))
            )

        if query.use_dense and self.vector_store is not None:
            source_results.append(
                ("dense", self.vector_store.search(query))
            )

        return source_results

    def _fuse_results(
        self,
        source_results: list[tuple[str, list[RetrievedChunk]]],
    ) -> list[RetrievedChunk]:
        fused_by_chunk_id: dict[str, RetrievedChunk] = {}

        for source_name, chunks in source_results:
            for rank, chunk in enumerate(chunks, start=1):
                fused_score = 1.0 / (self.rrf_constant + rank)
                existing = fused_by_chunk_id.get(chunk.chunk_id)
                if existing is None:
                    fused_by_chunk_id[chunk.chunk_id] = self._clone_chunk(
                        chunk,
                        score=fused_score,
                        retrieval_source=source_name,
                    )
                    continue

                existing.score += fused_score
                existing.metadata["fused_score"] = f"{existing.score:.12f}"
                existing.metadata["best_source_score"] = str(
                    max(
                        float(existing.metadata.get("best_source_score", "0") or 0),
                        chunk.score,
                    )
                )
                existing_sources = set(
                    str(existing.metadata.get("retrieval_sources", "")).split(",")
                ) - {""}
                existing_sources.add(source_name)
                existing.metadata[f"{source_name}_source_score"] = str(chunk.score)
                existing.metadata["retrieval_sources"] = ",".join(
                    sorted(existing_sources)
                )
                existing.retrieval_source = (
                    "hybrid"
                    if len(existing_sources) > 1
                    else source_name
                )

        return sorted(
            fused_by_chunk_id.values(),
            key=lambda chunk: chunk.score,
            reverse=True,
        )

    @staticmethod
    def _clone_chunk(
        chunk: RetrievedChunk,
        *,
        score: float,
        retrieval_source: str,
    ) -> RetrievedChunk:
        metadata = dict(chunk.metadata)
        metadata["retrieval_sources"] = retrieval_source
        metadata["best_source_score"] = str(chunk.score)
        metadata["fused_score"] = f"{score:.12f}"
        metadata[f"{retrieval_source}_source_score"] = str(chunk.score)

        return RetrievedChunk(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            content=chunk.content,
            score=score,
            retrieval_source=retrieval_source,
            chunk_type=chunk.chunk_type,
            section_id=chunk.section_id,
            section_path=list(chunk.section_path),
            source=chunk.source,
            citation=chunk.citation,
            metadata=metadata,
        )

    @classmethod
    def _prepare_for_reranking(
        cls,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                score=cls._best_source_score(chunk),
                retrieval_source=chunk.retrieval_source,
                chunk_type=chunk.chunk_type,
                section_id=chunk.section_id,
                section_path=list(chunk.section_path),
                source=chunk.source,
                citation=chunk.citation,
                metadata=dict(chunk.metadata),
            )
            for chunk in chunks
        ]

    @staticmethod
    def _best_source_score(chunk: RetrievedChunk) -> float:
        raw_score = chunk.metadata.get("best_source_score")
        if raw_score is None:
            return chunk.score

        try:
            return float(raw_score)
        except (TypeError, ValueError):
            return chunk.score
