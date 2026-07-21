from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.common import ChunkType


def context_priority(
    *,
    relation: str,
    query_intent: RetrievalQueryIntent,
    document_chunk,
) -> int:
    relation_priority = {
        "same_section_part": 100,
        "ancestor_overview": 94,
        "descendant_detail": 92,
        "asset_companion": 90,
        "sibling_section": 70,
        "neighbor": 60,
    }
    priority = relation_priority.get(relation, 50)

    if query_intent in {
        RetrievalQueryIntent.TABLE,
        RetrievalQueryIntent.FIGURE,
        RetrievalQueryIntent.SPECIFICATION,
    }:
        if relation == "asset_companion":
            priority += 20
        if document_chunk.chunk_type in {
            ChunkType.SPARE_PARTS_TABLE,
            ChunkType.DRAWING_REFERENCE,
            ChunkType.TECHNICAL_SPECIFICATION,
        }:
            priority += 10

    if query_intent == RetrievalQueryIntent.OVERVIEW:
        if relation == "same_section_part":
            priority += 8
        if relation == "ancestor_overview":
            priority += 20
        if relation == "descendant_detail":
            priority += 10

    if query_intent in {
        RetrievalQueryIntent.PROCEDURE,
        RetrievalQueryIntent.TROUBLESHOOTING,
        RetrievalQueryIntent.SAFETY,
    }:
        if relation == "same_section_part":
            priority += 15
        if relation in {"ancestor_overview", "descendant_detail"}:
            priority += 12
        if relation == "sibling_section":
            priority += 8

    return priority
