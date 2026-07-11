from src.application.workflows.retrieval.deduplication import (
    RetrievedChunkDeduplicator,
)

from src.domain.common import ChunkType, SourceLocation

from src.domain.retrieval import RetrievalQuery, RetrievedChunk

def make_query(
    *,
    query_text: str = "When should the hydraulic filter be replaced?",
    detected_identifiers: list[str] | None = None,
) -> RetrievalQuery:
    return RetrievalQuery(
        query_id="query_001",
        query_text=query_text,
        detected_identifiers=detected_identifiers or [],
        top_k=5,
    )

def make_chunk(
    *,
    chunk_id: str,
    content: str,
    score: float = 0.9,
    document_id: str = "doc_001",
    retrieval_source: str = "dense",
    chunk_type: ChunkType = ChunkType.GENERAL,
    section_id: str | None = "sec_001",
    section_path: list[str] | None = None,
    page: int = 1,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        score=score,
        retrieval_source=retrieval_source,
        chunk_type=chunk_type,
        section_id=section_id,
        section_path=section_path or ["Section"],
        source=SourceLocation(page_start=page, page_end=page),
        metadata=metadata or {},
    )

def test_group_order_matches_original_chunk_order_across_interleaved_documents() -> None:
    """Chunks are bucketed by document_id internally for comparison, but the
    returned groups must still reflect the order chunks first appeared in
    the input -- not the internal per-document bucketing order."""
    deduplicator = RetrievedChunkDeduplicator()
    query = make_query()
    chunks = [
        make_chunk(chunk_id="doc_a_1", content="Unique content A1.", document_id="doc_a"),
        make_chunk(chunk_id="doc_b_1", content="Unique content B1.", document_id="doc_b"),
        make_chunk(chunk_id="doc_a_2", content="Unique content A2.", document_id="doc_a"),
        make_chunk(chunk_id="doc_b_2", content="Unique content B2.", document_id="doc_b"),
    ]

    result = deduplicator.deduplicate(query=query, chunks=chunks)

    assert [group.representative.chunk_id for group in result.groups] == [
        "doc_a_1",
        "doc_b_1",
        "doc_a_2",
        "doc_b_2",
    ]
