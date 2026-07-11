from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.retrieval import RetrievedChunk


def to_retrieved_chunk(
    *,
    document_chunk,
    anchor_chunk: RetrievedChunk,
    relation: str,
    distance: int,
    query_intent: RetrievalQueryIntent,
) -> RetrievedChunk:
    metadata = {
        "anchor_chunk_id": anchor_chunk.chunk_id,
        "context_distance": str(distance),
        "context_relation": relation,
        "query_intent": query_intent.value,
    }

    return RetrievedChunk(
        chunk_id=document_chunk.chunk_id,
        document_id=document_chunk.document_id,
        content=document_chunk.content,
        score=max(anchor_chunk.score - (distance * 0.01), 0.0),
        retrieval_source="context_expansion",
        chunk_type=document_chunk.chunk_type,
        section_id=document_chunk.section_id,
        section_path=list(document_chunk.section_path),
        source=document_chunk.source,
        statistics=document_chunk.statistics,
        metadata=metadata,
    )
