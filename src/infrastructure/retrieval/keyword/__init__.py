__all__ = ["SqlKeywordIndex"]


def __getattr__(name: str):
    if name == "SqlKeywordIndex":
        from src.infrastructure.retrieval.keyword.sql_keyword_index import (
            SqlKeywordIndex,
        )

        return SqlKeywordIndex
    raise AttributeError(name)
