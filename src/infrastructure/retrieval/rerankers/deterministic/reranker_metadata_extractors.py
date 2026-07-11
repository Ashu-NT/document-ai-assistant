from src.domain.retrieval import RetrievedChunk
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import normalize_query_text


def metadata_float(
    chunk: RetrievedChunk,
    key: str,
    *,
    default: float = 0.0,
) -> float:
    raw_value = chunk.metadata.get(key)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return default


def metadata_int(
    chunk: RetrievedChunk,
    key: str,
    *,
    default: int = 0,
) -> int:
    raw_value = chunk.metadata.get(key)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return default


def identifier_match_count(
    chunk: RetrievedChunk,
    query_identifiers: set[str],
) -> int:
    if not query_identifiers:
        return 0
    lowered_content = chunk.content.lower()
    return sum(1 for identifier in query_identifiers if identifier in lowered_content)


def section_path_hit_count(
    chunk: RetrievedChunk,
    query_terms: list[str],
) -> int:
    normalized_path = normalize_query_text(chunk.section_path_text())
    return sum(1 for term in query_terms if term in normalized_path)
