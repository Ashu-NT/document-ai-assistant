from src.application.workflows.retrieval import RetrievalContextExpander
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


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
    section_id: str = "sec_001",
    section_path: list[str] | None = None,
    chunk_type: ChunkType = ChunkType.GENERAL,
    table_ids: list[str] | None = None,
    picture_ids: list[str] | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=section_id,
        content=f"Chunk {sequence_number} content",
        chunk_type=chunk_type,
        section_path=section_path or ["Procedure"],
        table_ids=table_ids or [],
        picture_ids=picture_ids or [],
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


def test_retrieval_context_expander_adds_ancestor_overview_for_detail_chunk() -> None:
    document_chunks = [
        make_document_chunk(
            chunk_id="chunk_overview",
            sequence_number=1,
            section_id="sec_root",
            section_path=["Procedure"],
            chunk_type=ChunkType.OVERVIEW,
        ),
        make_document_chunk(
            chunk_id="chunk_detail",
            sequence_number=2,
            section_id="sec_child",
            section_path=["Procedure", "Execution"],
            chunk_type=ChunkType.GENERAL,
        ),
    ]
    lookup_service = FakeDocumentLookupService({"doc_001": document_chunks})
    expander = RetrievalContextExpander(
        document_lookup_service=lookup_service,
        neighbor_window=0,
        max_context_chunks=3,
    )
    anchor = RetrievedChunk(
        chunk_id="chunk_detail",
        document_id="doc_001",
        content="Chunk 2 content",
        score=0.82,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_id="sec_child",
        section_path=["Procedure", "Execution"],
        source=SourceLocation(page_start=2, page_end=2),
    )

    expanded = expander.expand([anchor])

    assert [chunk.chunk_id for chunk in expanded] == [
        "chunk_detail",
        "chunk_overview",
    ]
    assert expanded[1].metadata["context_relation"] == "ancestor_overview"


def test_retrieval_context_expander_prioritizes_asset_companion_for_figure_query() -> None:
    document_chunks = [
        make_document_chunk(
            chunk_id="chunk_figure",
            sequence_number=3,
            section_id="sec_fig",
            section_path=["Procedure", "Assembly View"],
            chunk_type=ChunkType.DRAWING_REFERENCE,
            picture_ids=["pic_001"],
        ),
        make_document_chunk(
            chunk_id="chunk_text",
            sequence_number=4,
            section_id="sec_fig",
            section_path=["Procedure", "Assembly View"],
            chunk_type=ChunkType.GENERAL,
            picture_ids=["pic_001"],
        ),
        make_document_chunk(
            chunk_id="chunk_neighbor",
            sequence_number=5,
            section_id="sec_other",
            section_path=["Procedure", "Next Step"],
            chunk_type=ChunkType.GENERAL,
        ),
    ]
    lookup_service = FakeDocumentLookupService({"doc_001": document_chunks})
    expander = RetrievalContextExpander(
        document_lookup_service=lookup_service,
        neighbor_window=1,
        max_context_chunks=3,
    )
    anchor = RetrievedChunk(
        chunk_id="chunk_figure",
        document_id="doc_001",
        content="Figure chunk",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.DRAWING_REFERENCE,
        section_id="sec_fig",
        section_path=["Procedure", "Assembly View"],
        source=SourceLocation(page_start=3, page_end=3),
    )
    query = RetrievalQuery(
        query_id="query_figure_001",
        query_text="What does the figure show?",
    )

    expanded = expander.expand([anchor], query=query)

    assert [chunk.chunk_id for chunk in expanded] == [
        "chunk_figure",
        "chunk_text",
        "chunk_neighbor",
    ]
    assert expanded[1].metadata["context_relation"] == "asset_companion"
