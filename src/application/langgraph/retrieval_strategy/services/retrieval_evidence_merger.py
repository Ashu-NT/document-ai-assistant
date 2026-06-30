from __future__ import annotations

from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class RetrievalEvidenceMerger:
    def merge(
        self,
        *,
        chunks: list[RetrievedChunk],
        primary_strategy: RetrievalStrategy,
        max_chunks: int,
    ) -> list[RetrievedChunk]:
        deduped: dict[str, RetrievedChunk] = {}
        for chunk in chunks:
            existing = deduped.get(chunk.chunk_id)
            if existing is None:
                deduped[chunk.chunk_id] = chunk
                continue
            if chunk.score > existing.score:
                deduped[chunk.chunk_id] = chunk

        merged = list(deduped.values())
        merged.sort(
            key=lambda item: (
                -self._strategy_rank(item, primary_strategy),
                -item.score,
                item.source.page_start or 10**6,
                item.source.page_end or 10**6,
            )
        )
        return merged[:max_chunks]

    @staticmethod
    def _strategy_rank(
        chunk: RetrievedChunk,
        primary_strategy: RetrievalStrategy,
    ) -> int:
        strategy_value = chunk.metadata.get("retrieval_strategy")
        return 1 if strategy_value == primary_strategy.value else 0
