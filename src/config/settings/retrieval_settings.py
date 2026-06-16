from pydantic import Field
from pydantic_settings import BaseSettings


class RetrievalSettings(BaseSettings):
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

    class Config:
        env_file = ".env"
           