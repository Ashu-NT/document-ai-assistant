from src.application.workflows.retrieval import RetrievalContextExpander

from src.application.workflows.retrieval import RetrievalContextAssembler

from src.domain.common import ChunkType, SourceLocation

from src.domain.document import DocumentChunk

from src.domain.document.value_objects import ChunkStatistics

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
    chunk_index: int | None = None,
    chunk_total: int = 3,
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
        chunk_index=chunk_index or sequence_number,
        chunk_total=chunk_total,
    )

def test_retrieval_context_expander_adds_descendant_detail_for_overview_chunk() -> None:
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
            sequence_number=5,
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
        chunk_id="chunk_overview",
        document_id="doc_001",
        content="Overview chunk",
        score=0.82,
        retrieval_source="dense",
        chunk_type=ChunkType.OVERVIEW,
        section_id="sec_root",
        section_path=["Procedure"],
        source=SourceLocation(page_start=1, page_end=1),
    )

    expanded = expander.expand([anchor])

    assert [chunk.chunk_id for chunk in expanded] == [
        "chunk_overview",
        "chunk_detail",
    ]
    assert expanded[1].metadata["context_relation"] == "descendant_detail"

def test_retrieval_context_expander_adds_sibling_section_chunk() -> None:
    document_chunks = [
        make_document_chunk(
            chunk_id="chunk_sibling_a",
            sequence_number=1,
            section_id="sec_a",
            section_path=["Procedure", "StepA"],
        ),
        make_document_chunk(
            chunk_id="chunk_sibling_b",
            sequence_number=10,
            section_id="sec_b",
            section_path=["Procedure", "StepB"],
        ),
    ]
    lookup_service = FakeDocumentLookupService({"doc_001": document_chunks})
    expander = RetrievalContextExpander(
        document_lookup_service=lookup_service,
        neighbor_window=0,
        max_context_chunks=3,
    )
    anchor = RetrievedChunk(
        chunk_id="chunk_sibling_a",
        document_id="doc_001",
        content="Step A content",
        score=0.82,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_id="sec_a",
        section_path=["Procedure", "StepA"],
        source=SourceLocation(page_start=1, page_end=1),
    )

    expanded = expander.expand([anchor])

    assert [chunk.chunk_id for chunk in expanded] == [
        "chunk_sibling_a",
        "chunk_sibling_b",
    ]
    assert expanded[1].metadata["context_relation"] == "sibling_section"

def test_retrieval_context_expander_respects_token_budget() -> None:
    long_chunk = make_document_chunk(chunk_id="chunk_001", sequence_number=1)
    long_chunk.content = " ".join(["long"] * 30)
    long_chunk.statistics = ChunkStatistics(char_count=120, token_count_estimate=30)
    anchor_chunk = make_document_chunk(chunk_id="chunk_002", sequence_number=2)
    anchor_chunk.content = "short anchor text"
    anchor_chunk.statistics = ChunkStatistics(char_count=18, token_count_estimate=3)
    neighbor_chunk = make_document_chunk(
        chunk_id="chunk_003",
        sequence_number=3,
        section_id="sec_other",
        section_path=["Procedure", "Neighbor"],
    )
    neighbor_chunk.content = "short neighbor"
    neighbor_chunk.statistics = ChunkStatistics(char_count=14, token_count_estimate=2)
    lookup_service = FakeDocumentLookupService(
        {"doc_001": [long_chunk, anchor_chunk, neighbor_chunk]}
    )
    expander = RetrievalContextExpander(
        document_lookup_service=lookup_service,
        neighbor_window=1,
        max_context_chunks=3,
        context_assembler=RetrievalContextAssembler(token_budget=5),
    )
    anchor = RetrievedChunk(
        chunk_id="chunk_002",
        document_id="doc_001",
        content="short anchor text",
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
        "chunk_003",
    ]

def test_retrieval_context_expander_uses_anchor_retrieved_chunk_statistics() -> None:
    anchor_chunk = RetrievedChunk(
        chunk_id="chunk_anchor",
        document_id="doc_001",
        content="short anchor text",
        score=0.82,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_id="sec_anchor",
        section_path=["Procedure"],
        source=SourceLocation(page_start=2, page_end=2),
        statistics=ChunkStatistics(char_count=18, token_count_estimate=10),
    )
    document_anchor = make_document_chunk(
        chunk_id="chunk_anchor",
        sequence_number=2,
        section_id="sec_anchor",
        chunk_total=1,
    )
    document_anchor.statistics = ChunkStatistics(char_count=18, token_count_estimate=10)
    neighbor_chunk = make_document_chunk(
        chunk_id="chunk_neighbor",
        sequence_number=3,
        section_id="sec_other",
        section_path=["Procedure", "Neighbor"],
        chunk_total=1,
    )
    neighbor_chunk.statistics = ChunkStatistics(char_count=14, token_count_estimate=2)
    lookup_service = FakeDocumentLookupService(
        {"doc_001": [document_anchor, neighbor_chunk]}
    )
    expander = RetrievalContextExpander(
        document_lookup_service=lookup_service,
        neighbor_window=1,
        max_context_chunks=3,
        context_assembler=RetrievalContextAssembler(token_budget=11),
    )

    expanded = expander.expand([anchor_chunk])

    assert [chunk.chunk_id for chunk in expanded] == ["chunk_anchor"]
