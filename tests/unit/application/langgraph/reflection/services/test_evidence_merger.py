from src.application.langgraph.reflection.policies import RetrievalRetryPolicy
from src.application.langgraph.reflection.services import EvidenceMerger
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _chunk(chunk_id: str, *, score: float, document_id: str = "doc_1") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=f"content for {chunk_id}",
        score=score,
        retrieval_source="sql",
        chunk_type=ChunkType.GENERAL,
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_evidence_merger_preserves_initial_chunks_and_deduplicates_retry() -> None:
    merger = EvidenceMerger()

    merged, diagnostics = merger.merge(
        initial_chunks=[_chunk("chunk_1", score=0.9), _chunk("chunk_2", score=0.8)],
        retry_chunks=[_chunk("chunk_2", score=0.95), _chunk("chunk_3", score=0.7)],
        policy=RetrievalRetryPolicy(max_merged_chunks=12),
        document_id="doc_1",
    )

    assert [chunk.chunk_id for chunk in merged] == ["chunk_1", "chunk_2", "chunk_3"]
    assert diagnostics["merged_chunk_ids"] == ["chunk_1", "chunk_2", "chunk_3"]


def test_evidence_merger_filters_wrong_document_chunks() -> None:
    merger = EvidenceMerger()

    merged, diagnostics = merger.merge(
        initial_chunks=[_chunk("chunk_1", score=0.9, document_id="doc_1")],
        retry_chunks=[_chunk("chunk_2", score=0.8, document_id="doc_2")],
        policy=RetrievalRetryPolicy(max_merged_chunks=12),
        document_id="doc_1",
    )

    assert [chunk.chunk_id for chunk in merged] == ["chunk_1"]
    assert diagnostics["filtered_wrong_document_chunk_ids"] == ["chunk_2"]
