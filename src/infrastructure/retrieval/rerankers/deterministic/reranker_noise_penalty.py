from src.application.workflows.retrieval import RetrievalQueryIntent
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievedChunk
from src.infrastructure.retrieval.keyword.sql_keyword_query_terms import normalize_query_text

_NOISE_PATH_MARKERS = (
    "revision / modification table",
    "table of contents",
    "environmentally",
    "responsible solutions",
    "engineered",
)


def noise_penalty(chunk: RetrievedChunk) -> float:
    normalized_path = normalize_query_text(chunk.section_path_text())
    penalty = 0.0
    if any(marker in normalized_path for marker in _NOISE_PATH_MARKERS):
        penalty += 8.0
    return penalty


def intent_noise_penalty(
    *,
    intent: RetrievalQueryIntent,
    chunk_type: ChunkType,
    query_text: str,
    identifier_matches: int,
) -> float:
    if chunk_type == ChunkType.SPARE_PARTS_TABLE and intent not in {
        RetrievalQueryIntent.IDENTIFIER,
        RetrievalQueryIntent.TABLE,
        RetrievalQueryIntent.SPECIFICATION,
    }:
        return 18.0

    if chunk_type == ChunkType.DRAWING_REFERENCE and intent not in {
        RetrievalQueryIntent.IDENTIFIER,
        RetrievalQueryIntent.FIGURE,
    }:
        return 12.0

    if (
        intent == RetrievalQueryIntent.OVERVIEW
        and chunk_type == ChunkType.TECHNICAL_SPECIFICATION
        and "specification" not in query_text
    ):
        return 5.0

    return 0.0
