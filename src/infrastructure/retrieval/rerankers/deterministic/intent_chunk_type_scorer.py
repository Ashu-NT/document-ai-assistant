from src.application.workflows.retrieval import RetrievalQueryIntent
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery

_IDENTIFIER_FIT_TYPES = {
    ChunkType.SPARE_PARTS_TABLE,
    ChunkType.TECHNICAL_SPECIFICATION,
    ChunkType.CERTIFICATION_INFO,
    ChunkType.DRAWING_REFERENCE,
}


def intent_chunk_type_score(
    intent: RetrievalQueryIntent,
    chunk_type: ChunkType,
    query: RetrievalQuery,
    *,
    query_text: str,
) -> float:
    if query.chunk_types and chunk_type in query.chunk_types:
        base = 8.0
    else:
        base = 0.0

    if intent == RetrievalQueryIntent.IDENTIFIER:
        if chunk_type in _IDENTIFIER_FIT_TYPES:
            return base + 14.0
        if chunk_type == ChunkType.OVERVIEW:
            return base - 8.0
        if chunk_type == ChunkType.GENERAL:
            return base + 2.0
    if intent == RetrievalQueryIntent.TABLE:
        if chunk_type == ChunkType.SPARE_PARTS_TABLE:
            return base + 15.0
        if chunk_type in {ChunkType.TECHNICAL_SPECIFICATION, ChunkType.CERTIFICATION_INFO}:
            return base + 10.0
    if intent == RetrievalQueryIntent.SPECIFICATION:
        if chunk_type in {ChunkType.TECHNICAL_SPECIFICATION, ChunkType.CERTIFICATION_INFO}:
            return base + 15.0
        if chunk_type == ChunkType.MAINTENANCE_INTERVAL:
            return base + 12.0
        if chunk_type == ChunkType.OPERATION_INSTRUCTION and any(
            marker in query_text
            for marker in ("pressure", "torque", "set", "setting", "adjust", "optimis", "optimiz")
        ):
            return base + 10.0
        if chunk_type == ChunkType.SPARE_PARTS_TABLE:
            return base + 8.0
        if chunk_type == ChunkType.OVERVIEW:
            return base - 4.0
    if intent == RetrievalQueryIntent.PROCEDURE:
        if chunk_type == ChunkType.OPERATION_INSTRUCTION:
            return base + 16.0
        if chunk_type == ChunkType.MAINTENANCE_PROCEDURE:
            return base + 15.0
        if chunk_type == ChunkType.INSTALLATION_INSTRUCTION:
            return base + 14.0
        if chunk_type == ChunkType.MAINTENANCE_INTERVAL:
            return base + 12.0
        if chunk_type == ChunkType.TROUBLESHOOTING:
            return base + 9.0
        if chunk_type == ChunkType.TECHNICAL_SPECIFICATION and any(
            marker in query_text
            for marker in ("quantity", "pressure", "torque", "voltage", "current", "specification", "oil")
        ):
            return base + 7.0
        if chunk_type == ChunkType.OVERVIEW:
            return base - 8.0
        if chunk_type == ChunkType.GENERAL:
            return base + 1.0
    if intent == RetrievalQueryIntent.TROUBLESHOOTING:
        if chunk_type == ChunkType.TROUBLESHOOTING:
            return base + 16.0
        if chunk_type == ChunkType.OPERATION_INSTRUCTION:
            return base + 7.0
    if intent == RetrievalQueryIntent.SAFETY:
        if chunk_type == ChunkType.SAFETY_WARNING:
            return base + 14.0
        if chunk_type == ChunkType.OVERVIEW:
            return base - 4.0
    if intent == RetrievalQueryIntent.FIGURE:
        if chunk_type == ChunkType.DRAWING_REFERENCE:
            return base + 16.0
    if intent == RetrievalQueryIntent.OVERVIEW:
        if chunk_type == ChunkType.OVERVIEW:
            return base + 12.0
        if chunk_type == ChunkType.GENERAL:
            return base + 10.0
        if chunk_type in {
            ChunkType.OPERATION_INSTRUCTION,
            ChunkType.INSTALLATION_INSTRUCTION,
        }:
            return base + 4.0
        if chunk_type == ChunkType.TECHNICAL_SPECIFICATION:
            return base + 1.0
        if chunk_type in {
            ChunkType.SPARE_PARTS_TABLE,
            ChunkType.DRAWING_REFERENCE,
        }:
            return base - 12.0

    return base
