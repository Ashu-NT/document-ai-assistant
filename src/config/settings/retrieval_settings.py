from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class RetrievalSettings(AppBaseSettings):
    enable_dense_retrieval: bool = Field(
        alias="ENABLE_DENSE_RETRIEVAL"
    )

    enable_keyword_retrieval: bool = Field(
        alias="ENABLE_KEYWORD_RETRIEVAL"
    )

    enable_sql_retrieval: bool = Field(
        alias="ENABLE_SQL_RETRIEVAL"
    )

    enable_dense_identifier_filter: bool = Field(
        default=False,
        alias="ENABLE_DENSE_IDENTIFIER_FILTER",
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

    context_neighbor_window: int = Field(
        default=1,
        alias="RETRIEVAL_NEIGHBOR_WINDOW"
    )

    context_max_chunks: int = Field(
        default=8,
        alias="RETRIEVAL_MAX_CONTEXT_CHUNKS"
    )

    context_token_budget: int = Field(
        default=900,
        alias="RETRIEVAL_CONTEXT_TOKEN_BUDGET"
    )

    min_retrieval_score: float = Field(
        default=0.50,
        alias="RETRIEVAL_MIN_SCORE"
    )

    # Expands retrieved chunks with their linked table/figure/section
    # cross-references at query time (e.g. a chunk that says "see Table 4"
    # also pulls in Table 4). Defaults on: the ingest-time linking this
    # depends on (ChunkCrossReferenceLinker) is meaningless if nothing at
    # query time ever uses it.
    cross_reference_expansion_enabled: bool = Field(
        default=True,
        alias="RETRIEVAL_CROSS_REFERENCE_EXPANSION_ENABLED"
    )

    relevance_score_threshold: float = Field(
        default=0.40,
        alias="RETRIEVAL_RELEVANCE_SCORE_THRESHOLD"
    )

