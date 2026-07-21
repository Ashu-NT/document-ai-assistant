from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def to_retrieved_chunk(chunk) -> RetrievedChunk:
    """Converts a plain document chunk (e.g. fetched by chunk id from
    `DocumentLookupService`, not returned by normal retrieval) into the
    `RetrievedChunk` shape the rest of the answer-generation pipeline works
    with, so identifier/structured-entity source chunks can be joined into
    the same context as retrieved chunks.

    Builds a real `Citation` (mirroring context_chunk_converter.to_retrieved_
    chunk()) rather than leaving it unset -- these chunks now actually reach
    generation (see StructuredFactJoiner's allowed_chunk_ids fix), so a
    missing citation would show up as an uncredited source in the answer's
    reference notes."""
    return RetrievedChunk(
        chunk_id=chunk.chunk_id,
        document_id=chunk.document_id,
        content=chunk.content,
        score=1.0,
        retrieval_source="structured_lookup",
        chunk_type=chunk.chunk_type,
        section_id=chunk.section_id,
        section_path=list(chunk.section_path),
        source=chunk.source,
        citation=Citation(
            citation_id=f"cit_{chunk.chunk_id}",
            document_id=chunk.document_id,
            chunk_id=chunk.chunk_id,
            section_id=chunk.section_id,
            section_title=chunk.section_path[-1] if chunk.section_path else None,
            source=chunk.source,
        ),
        statistics=chunk.statistics,
        metadata={"sequence_number": str(chunk.sequence_number)},
    )
