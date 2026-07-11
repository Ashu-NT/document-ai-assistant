from __future__ import annotations

from dataclasses import replace

from src.domain.retrieval import RetrievalQuery


def _default_candidate_pool_top_k() -> int:
    try:
        from src.config.settings import retrieval_settings

        return max(
            retrieval_settings.final_retrieval_top_k,
            retrieval_settings.dense_retrieval_top_k,
            retrieval_settings.keyword_retrieval_top_k,
            retrieval_settings.sql_retrieval_top_k,
        )
    except Exception:
        return 10


class RetrievalCandidatePoolSizer:
    """Sizes the candidate pool fetched before dedup/rerank narrows it down."""

    def __init__(self, *, candidate_pool_top_k: int | None = None) -> None:
        self.candidate_pool_top_k = candidate_pool_top_k

    def candidate_query(self, query: RetrievalQuery) -> RetrievalQuery:
        candidate_pool_top_k = max(
            query.top_k,
            self.candidate_pool_top_k or _default_candidate_pool_top_k(),
        )
        if candidate_pool_top_k == query.top_k:
            return query
        return replace(query, top_k=candidate_pool_top_k)
