from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class RetrievalSettings(AppBaseSettings):
    top_k_retrieval: int = Field(alias="TOP_K_RETRIEVAL")

    retrieval_score_threshold: float = Field(
        alias="RETRIEVAL_SCORE_THRESHOLD"
    )

    rerank_top_k: int = Field(alias="RERANK_TOP_K")

    enable_dense_retrieval: bool = Field(
        alias="ENABLE_DENSE_RETRIEVAL"
    )

    enable_keyword_retrieval: bool = Field(
        alias="ENABLE_KEYWORD_RETRIEVAL"
    )

    enable_sql_retrieval: bool = Field(
        alias="ENABLE_SQL_RETRIEVAL"
    )

    dense_retrieval_top_k: int = Field(
        alias="DENSE_RETRIEVAL_TOP_K"
    )

    keyword_retrieval_top_k: int = Field(
        alias="KEYWORD_RETRIEVAL_TOP_K"
    )

    sql_retrieval_top_k: int = Field(
        alias="SQL_RETRIEVAL_TOP_K"
    )

    final_retrieval_top_k: int = Field(
        alias="FINAL_RETRIEVAL_TOP_K"
    )

    exact_duplicate_enabled: bool = Field(
        default=True,
        alias="RETRIEVAL_EXACT_DUPLICATE_ENABLED"
    )

    context_companion_collapse_enabled: bool = Field(
        default=True,
        alias="RETRIEVAL_CONTEXT_COMPANION_COLLAPSE_ENABLED"
    )

    overview_duplicate_collapse_enabled: bool = Field(
        default=True,
        alias="RETRIEVAL_OVERVIEW_DUPLICATE_COLLAPSE_ENABLED"
    )

    token_overlap_threshold: float = Field(
        default=0.90,
        alias="RETRIEVAL_TOKEN_OVERLAP_THRESHOLD"
    )

    containment_threshold: float = Field(
        default=0.95,
        alias="RETRIEVAL_CONTAINMENT_THRESHOLD"
    )

    min_unique_token_count: int = Field(
        default=20,
        alias="RETRIEVAL_MIN_UNIQUE_TOKEN_COUNT"
    )

           
