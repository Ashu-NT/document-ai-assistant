from src.domain.common import ChunkType
from src.infrastructure.retrieval.keyword.scoring.sql_keyword_scoring_config import (
    FIGURE_QUERY_MARKERS,
    NOISE_SECTION_TOKENS,
    OVERVIEW_QUERY_MARKERS,
    OVERVIEW_SECTION_MARKERS,
    TABLE_QUERY_MARKERS,
)
from src.infrastructure.retrieval.keyword.scoring.sql_keyword_text_helpers import (
    looks_like_toc_content,
)
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import (
    normalize_query_text,
)


def chunk_role_penalty(chunk_role: str) -> float:
    penalties = {
        "atomic_evidence": 0.0,
        "context_companion": 2.5,
        "asset_companion": 1.5,
        "overview_companion": 5.0,
    }
    return penalties.get(chunk_role, 0.0)


def ancestor_specificity_bonus(*, chunk_type: str, query_text: str) -> float:
    if chunk_type == ChunkType.MAINTENANCE_INTERVAL.value and any(
        marker in query_text
        for marker in ("maintenance", "interval", "lubrication", "service")
    ):
        return 2.5
    if any(marker in query_text for marker in OVERVIEW_QUERY_MARKERS):
        return 2.0
    return 1.5


def overview_section_bonus(
    *,
    normalized_local: str,
    normalized_ancestor: str,
) -> float:
    if any(marker in normalized_local for marker in OVERVIEW_SECTION_MARKERS):
        return 5.0
    if any(marker in normalized_ancestor for marker in OVERVIEW_SECTION_MARKERS):
        return 2.0
    return 0.0


def noise_penalty(
    *,
    chunk_type: str,
    section_path_text: str,
    content: str,
    query_text: str,
    exact_identifier_matches: int,
) -> float:
    normalized_path = normalize_query_text(section_path_text)
    normalized_content = normalize_query_text(content)
    lowered_query = query_text.lower()

    penalty = 0.0
    if "table of contents" in normalized_path or looks_like_toc_content(content):
        penalty += 14.0
    if (
        "revision modification table" in normalized_path
        and "revision" not in lowered_query
        and "modification" not in lowered_query
    ):
        penalty += 12.0
    if exact_identifier_matches == 0 and any(
        token in normalized_path for token in NOISE_SECTION_TOKENS
    ):
        penalty += 8.0
    if (
        exact_identifier_matches == 0
        and normalized_content.count("fundamentalmarinedevelopments") > 0
    ):
        penalty += 4.0
    if exact_identifier_matches == 0 and chunk_type == ChunkType.SPARE_PARTS_TABLE.value:
        if not any(marker in lowered_query for marker in TABLE_QUERY_MARKERS):
            penalty += 12.0
        if any(marker in lowered_query for marker in OVERVIEW_QUERY_MARKERS):
            penalty += 6.0
    if (
        exact_identifier_matches == 0
        and chunk_type == ChunkType.DRAWING_REFERENCE.value
        and not any(marker in lowered_query for marker in FIGURE_QUERY_MARKERS)
    ):
        penalty += 8.0
    if (
        exact_identifier_matches == 0
        and chunk_type == ChunkType.TECHNICAL_SPECIFICATION.value
        and any(marker in lowered_query for marker in OVERVIEW_QUERY_MARKERS)
    ):
        penalty += 4.0
    return penalty
