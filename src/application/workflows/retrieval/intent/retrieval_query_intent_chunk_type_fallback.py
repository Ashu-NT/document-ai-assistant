from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery


def infer_from_chunk_types(query: RetrievalQuery) -> RetrievalQueryIntent | None:
    if ChunkType.SPARE_PARTS_TABLE in query.chunk_types:
        return RetrievalQueryIntent.TABLE
    if ChunkType.DRAWING_REFERENCE in query.chunk_types:
        return RetrievalQueryIntent.FIGURE
    if ChunkType.SAFETY_WARNING in query.chunk_types:
        return RetrievalQueryIntent.SAFETY
    if ChunkType.TROUBLESHOOTING in query.chunk_types:
        return RetrievalQueryIntent.TROUBLESHOOTING
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.MAINTENANCE_INTERVAL,
            ChunkType.MAINTENANCE_PROCEDURE,
        }
    ):
        return RetrievalQueryIntent.MAINTENANCE
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.INSTALLATION_INSTRUCTION,
            ChunkType.OPERATION_INSTRUCTION,
        }
    ):
        return RetrievalQueryIntent.PROCEDURE
    if any(
        chunk_type in query.chunk_types
        for chunk_type in {
            ChunkType.TECHNICAL_SPECIFICATION,
            ChunkType.CERTIFICATION_INFO,
        }
    ):
        return RetrievalQueryIntent.SPECIFICATION
    return None
