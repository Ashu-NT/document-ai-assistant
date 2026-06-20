from src.application.workflows.retrieval import RetrievalContextExpander
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.domain.retrieval import RetrievedChunk


class FakeDocumentLookupService:
    def __init__(self, chunks_by_document: dict[str, list[DocumentChunk]]) -> None:
        self.chunks_by_document = chunks_by_document
        self.calls: list[str] = []

    def list_chunks_by_document(self, document_id: str) -> list[DocumentChunk]:
        self.calls.append(document_id)
        return self.chunks_by_document[document_id]


def make_document_chunk(
    *,
    chunk_id: str,
    sequence_number: int,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=f"Chunk {sequence_number} content",
        chunk_type=ChunkType.GENERAL,
        section_path=["Procedure"],
        source=SourceLocation(page_start=sequence_number, page_end=sequence_number),
        sequence_number=sequence_number,
        chunk_index=sequence_number,
        chunk_total=3,
    )


def test_retrieval_context_expander_adds_neighboring_chunks() -> None:
    document_chunks = [
        make_document_chunk(chunk_id="chunk_001", sequence_number=1),
        make_document_chunk(chunk_id="chunk_002", sequence_number=2),
        make_document_chunk(chunk_id="chunk_003", sequence_number=3),
    ]
    lookup_service = FakeDocumentLookupService({"doc_001": document_chunks})
    expander = RetrievalContextExpander(
        document_lookup_service=lookup_service,
        neighbor_window=1,
    )
    anchor = RetrievedChunk(
        chunk_id="chunk_002",
        document_id="doc_001",
        content="Chunk 2 content",
        score=0.82,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_id="sec_001",
        section_path=["Procedure"],
        source=SourceLocation(page_start=2, page_end=2),
    )

    expanded = expander.expand([anchor])

    assert [chunk.chunk_id for chunk in expanded] == [
        "chunk_002",
        "chunk_001",
        "chunk_003",
    ]
    assert lookup_service.calls == ["doc_001"]
    assert expanded[1].retrieval_source == "context_expansion"
    assert expanded[1].metadata["anchor_chunk_id"] == "chunk_002"
    assert expanded[1].metadata["context_distance"] == "1"


def test_retrieval_context_expander_returns_original_chunks_when_disabled() -> None:
    anchor = RetrievedChunk(
        chunk_id="chunk_002",
        document_id="doc_001",
        content="Chunk 2 content",
        score=0.82,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_id="sec_001",
        section_path=["Procedure"],
        source=SourceLocation(page_start=2, page_end=2),
    )
    expander = RetrievalContextExpander(
        document_lookup_service=FakeDocumentLookupService({"doc_001": []}),
        neighbor_window=0,
    )

    expanded = expander.expand([anchor])

    assert expanded == [anchor]
