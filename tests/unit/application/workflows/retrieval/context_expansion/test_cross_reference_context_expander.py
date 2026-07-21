from src.application.workflows.retrieval import CrossReferenceContextExpander
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    Document,
    DocumentChunk,
    DocumentGraph,
    DocumentHashes,
)
from src.domain.retrieval import RetrievedChunk


class FakeDocumentLookupService:
    def __init__(self, graphs_by_document: dict[str, DocumentGraph]) -> None:
        self.graphs_by_document = graphs_by_document
        self.calls: list[str] = []

    def get_document_graph(self, document_id: str):
        self.calls.append(document_id)
        return self.graphs_by_document.get(document_id)


def make_document_chunk(
    *,
    chunk_id: str,
    page_start: int,
    chunk_type: ChunkType = ChunkType.GENERAL,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content=f"Content for {chunk_id}",
        chunk_type=chunk_type,
        source=SourceLocation(page_start=page_start, page_end=page_start),
    )


def make_graph(
    *,
    chunks: list[DocumentChunk],
    cross_references: list[ChunkCrossReference],
) -> DocumentGraph:
    graph = DocumentGraph(
        document=Document(
            document_id="doc_001",
            file_name="f.pdf",
            file_path="f.pdf",
            hashes=DocumentHashes(file_hash="h", content_hash="c"),
        )
    )
    for chunk in chunks:
        graph.add_chunk(chunk)
    for cross_reference in cross_references:
        graph.add_cross_reference(cross_reference)
    return graph


def make_anchor(*, chunk_id: str, page_start: int) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=f"Content for {chunk_id}",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.TROUBLESHOOTING,
        source=SourceLocation(page_start=page_start, page_end=page_start),
    )


def test_expand_adds_the_resolved_referenced_chunk() -> None:
    target_chunk = make_document_chunk(
        chunk_id="chunk_procedure",
        page_start=42,
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
    )
    source_chunk = make_document_chunk(chunk_id="chunk_source", page_start=5)
    cross_reference = ChunkCrossReference(
        cross_reference_id="xref_1",
        document_id="doc_001",
        source_chunk_id="chunk_source",
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        matched_text="(→ Page 42)",
        target_page=42,
        target_chunk_id="chunk_procedure",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
        confidence_score=0.9,
    )
    graph = make_graph(
        chunks=[source_chunk, target_chunk], cross_references=[cross_reference]
    )
    lookup_service = FakeDocumentLookupService({"doc_001": graph})
    expander = CrossReferenceContextExpander(document_lookup_service=lookup_service)

    anchor = make_anchor(chunk_id="chunk_source", page_start=5)
    result = expander.expand([anchor], query=None)

    assert len(result) == 2
    added = result[1]
    assert added.chunk_id == "chunk_procedure"
    assert added.metadata["context_relation"] == "referenced_procedure"


def test_expand_does_not_add_anything_for_an_unresolved_reference() -> None:
    source_chunk = make_document_chunk(chunk_id="chunk_source", page_start=5)
    cross_reference = ChunkCrossReference(
        cross_reference_id="xref_1",
        document_id="doc_001",
        source_chunk_id="chunk_source",
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        matched_text="(→ Page 999)",
        target_page=999,
        target_chunk_id=None,
        resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
        confidence_score=0.0,
    )
    graph = make_graph(chunks=[source_chunk], cross_references=[cross_reference])
    lookup_service = FakeDocumentLookupService({"doc_001": graph})
    expander = CrossReferenceContextExpander(document_lookup_service=lookup_service)

    anchor = make_anchor(chunk_id="chunk_source", page_start=5)
    result = expander.expand([anchor], query=None)

    assert len(result) == 1
    assert result[0].chunk_id == "chunk_source"


def test_expand_does_not_duplicate_a_target_already_present_in_the_retrieved_set() -> (
    None
):
    target_chunk = make_document_chunk(
        chunk_id="chunk_procedure",
        page_start=42,
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
    )
    source_chunk = make_document_chunk(chunk_id="chunk_source", page_start=5)
    cross_reference = ChunkCrossReference(
        cross_reference_id="xref_1",
        document_id="doc_001",
        source_chunk_id="chunk_source",
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        matched_text="(→ Page 42)",
        target_page=42,
        target_chunk_id="chunk_procedure",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
        confidence_score=0.9,
    )
    graph = make_graph(
        chunks=[source_chunk, target_chunk], cross_references=[cross_reference]
    )
    lookup_service = FakeDocumentLookupService({"doc_001": graph})
    expander = CrossReferenceContextExpander(document_lookup_service=lookup_service)

    anchor = make_anchor(chunk_id="chunk_source", page_start=5)
    already_present = make_anchor(chunk_id="chunk_procedure", page_start=42)
    result = expander.expand([anchor, already_present], query=None)

    assert len(result) == 2
    assert [chunk.chunk_id for chunk in result] == ["chunk_source", "chunk_procedure"]


def test_expand_returns_input_unchanged_when_document_graph_is_missing() -> None:
    lookup_service = FakeDocumentLookupService({})
    expander = CrossReferenceContextExpander(document_lookup_service=lookup_service)

    anchor = make_anchor(chunk_id="chunk_source", page_start=5)
    result = expander.expand([anchor], query=None)

    assert result == [anchor]


def test_expand_returns_empty_list_for_empty_input() -> None:
    lookup_service = FakeDocumentLookupService({})
    expander = CrossReferenceContextExpander(document_lookup_service=lookup_service)

    assert expander.expand([], query=None) == []
