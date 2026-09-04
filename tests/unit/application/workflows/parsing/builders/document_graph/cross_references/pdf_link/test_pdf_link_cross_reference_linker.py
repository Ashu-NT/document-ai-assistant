from src.application.contracts.pdf_links import PdfLinkAnnotation, PdfLinkExtractionResult
from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.pdf_link_cross_reference_linker import (
    PdfLinkCrossReferenceLinker,
)
from src.domain.common import BoundingBox, DocumentType, SourceLocation
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.document.entities import (
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
)
from src.domain.document.entities.chunk import DocumentChunk
from src.domain.document.entities.document import Document
from src.domain.document.value_objects import DocumentHashes
from src.shared.ids import IdGenerator


def make_chunk(*, chunk_id: str, page_start: int, page_end: int | None = None) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content="content",
        source=SourceLocation(page_start=page_start, page_end=page_end or page_start),
        sequence_number=1,
    )


def make_graph(chunks: list[DocumentChunk]) -> DocumentGraph:
    document = Document(
        document_id="doc_001",
        file_name="manual.pdf",
        file_path="data/input/manual.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="c1"),
        document_type=DocumentType.MANUAL,
    )
    graph = DocumentGraph(document=document)
    for chunk in chunks:
        graph.add_chunk(chunk)
    return graph


def make_annotation(
    *, source_page: int, dest_page: int, link_kind: str = "goto"
) -> PdfLinkAnnotation:
    return PdfLinkAnnotation(
        source_page=source_page,
        dest_page=dest_page,
        link_kind=link_kind,
        source_rect=BoundingBox(x1=0.0, y1=0.0, x2=1.0, y2=1.0),
        rect_coordinate_origin="pdf_native_bottom_left",
        source_page_size=(612.0, 792.0),
        source_page_rotation_degrees=0,
        source_page_label=str(source_page),
        dest_page_label=str(dest_page),
    )


def _linker() -> PdfLinkCrossReferenceLinker:
    return PdfLinkCrossReferenceLinker(id_generator=IdGenerator())


def test_link_resolves_a_unique_source_and_dest_chunk() -> None:
    graph = make_graph(
        [make_chunk(chunk_id="source", page_start=1), make_chunk(chunk_id="target", page_start=49)]
    )
    extraction_result = PdfLinkExtractionResult(
        annotations=[make_annotation(source_page=1, dest_page=49)]
    )

    result = _linker().link(graph, extraction_result)

    assert len(result.references) == 1
    reference = result.references[0]
    assert reference.reference_type == ChunkCrossReferenceType.PDF_LINK_REFERENCE
    assert reference.source_chunk_id == "source"
    assert reference.target_chunk_id == "target"
    assert reference.target_page == 49
    assert reference.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE
    assert reference.confidence_score == 0.9
    assert reference.matched_text == "pdf_link_annotation"
    assert reference.link_provenance.source_page == 1
    assert reference.link_provenance.link_kind == "goto"
    assert result.diagnostics.unresolved_count == 0
    assert result.diagnostics.ambiguous_count == 0
    assert result.diagnostics.self_reference_count == 0
    assert result.diagnostics.duplicate_count == 0


def test_link_counts_unresolved_when_no_chunk_covers_source_or_dest_page() -> None:
    graph = make_graph([make_chunk(chunk_id="source", page_start=1)])
    extraction_result = PdfLinkExtractionResult(
        annotations=[make_annotation(source_page=1, dest_page=999)]
    )

    result = _linker().link(graph, extraction_result)

    assert result.references == []
    assert result.diagnostics.unresolved_count == 1


def test_link_counts_ambiguous_with_no_tie_break_when_multiple_chunks_share_a_page() -> (
    None
):
    graph = make_graph(
        [
            make_chunk(chunk_id="source", page_start=1),
            make_chunk(chunk_id="target_a", page_start=49),
            make_chunk(chunk_id="target_b", page_start=49),
        ]
    )
    extraction_result = PdfLinkExtractionResult(
        annotations=[make_annotation(source_page=1, dest_page=49)]
    )

    result = _linker().link(graph, extraction_result)

    assert result.references == []
    assert result.diagnostics.ambiguous_count == 1


def test_link_counts_self_reference_when_source_and_dest_are_the_same_chunk() -> None:
    graph = make_graph([make_chunk(chunk_id="only", page_start=1, page_end=5)])
    extraction_result = PdfLinkExtractionResult(
        annotations=[make_annotation(source_page=1, dest_page=3)]
    )

    result = _linker().link(graph, extraction_result)

    assert result.references == []
    assert result.diagnostics.self_reference_count == 1


def test_link_counts_duplicate_when_the_same_pair_resolves_twice() -> None:
    graph = make_graph(
        [make_chunk(chunk_id="source", page_start=1), make_chunk(chunk_id="target", page_start=49)]
    )
    extraction_result = PdfLinkExtractionResult(
        annotations=[
            make_annotation(source_page=1, dest_page=49),
            make_annotation(source_page=1, dest_page=49, link_kind="direct_destination"),
        ]
    )

    result = _linker().link(graph, extraction_result)

    assert len(result.references) == 1
    assert result.diagnostics.duplicate_count == 1


def test_linker_does_not_mutate_graph() -> None:
    graph = make_graph(
        [make_chunk(chunk_id="source", page_start=1), make_chunk(chunk_id="target", page_start=49)]
    )
    extraction_result = PdfLinkExtractionResult(
        annotations=[make_annotation(source_page=1, dest_page=49)]
    )

    _linker().link(graph, extraction_result)

    assert graph.cross_references == {}
