from __future__ import annotations

from src.application.workflows.retrieval.deduplication.retrieval_deduplication_policy import (
    RetrievalDeduplicationPolicy,
)


def build_default_retrieval_deduplication_policy() -> RetrievalDeduplicationPolicy:
    try:
        from src.config.settings import retrieval_settings

        return RetrievalDeduplicationPolicy(
            exact_duplicate_enabled=retrieval_settings.exact_duplicate_enabled,
            context_companion_collapse_enabled=(
                retrieval_settings.context_companion_collapse_enabled
            ),
            overview_duplicate_collapse_enabled=(
                retrieval_settings.overview_duplicate_collapse_enabled
            ),
            token_overlap_threshold=retrieval_settings.token_overlap_threshold,
            containment_threshold=retrieval_settings.containment_threshold,
            min_unique_token_count=retrieval_settings.min_unique_token_count,
        )
    except Exception:
        return RetrievalDeduplicationPolicy()
