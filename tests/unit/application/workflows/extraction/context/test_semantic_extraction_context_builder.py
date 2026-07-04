from src.application.workflows.extraction.context.semantic_extraction_context_builder import (
    SemanticExtractionContextBuilder,
)
from src.domain.common import SourceLocation
from src.domain.document import DocumentChunk, DocumentSection


def make_chunk(chunk_id: str, *, chunk_index: int, section_id: str | None = "section_001") -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="document_001",
        section_id=section_id,
        content=f"Content for {chunk_id}.",
        section_path=["4", "Maintenance"],
        element_ids=[f"el_{chunk_index}"],
        source=SourceLocation(page_start=4, page_end=4),
        chunk_index=chunk_index,
    )


def test_build_all_returns_one_context_per_chunk() -> None:
    chunks = [make_chunk("chunk_001", chunk_index=1), make_chunk("chunk_002", chunk_index=2)]

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001", chunks=chunks
    )

    assert set(contexts) == {"chunk_001", "chunk_002"}


def test_first_chunk_only_has_a_next_neighbor() -> None:
    chunks = [
        make_chunk("chunk_001", chunk_index=1),
        make_chunk("chunk_002", chunk_index=2),
        make_chunk("chunk_003", chunk_index=3),
    ]

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001", chunks=chunks
    )

    assert contexts["chunk_001"].nearby_chunk_ids == ("chunk_002",)


def test_middle_chunk_has_both_neighbors() -> None:
    chunks = [
        make_chunk("chunk_001", chunk_index=1),
        make_chunk("chunk_002", chunk_index=2),
        make_chunk("chunk_003", chunk_index=3),
    ]

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001", chunks=chunks
    )

    assert contexts["chunk_002"].nearby_chunk_ids == ("chunk_001", "chunk_003")


def test_last_chunk_only_has_a_previous_neighbor() -> None:
    chunks = [
        make_chunk("chunk_001", chunk_index=1),
        make_chunk("chunk_002", chunk_index=2),
        make_chunk("chunk_003", chunk_index=3),
    ]

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001", chunks=chunks
    )

    assert contexts["chunk_003"].nearby_chunk_ids == ("chunk_002",)


def test_neighbor_resolution_respects_chunk_index_not_list_order() -> None:
    # Deliberately out of order in the input list.
    chunks = [
        make_chunk("chunk_003", chunk_index=3),
        make_chunk("chunk_001", chunk_index=1),
        make_chunk("chunk_002", chunk_index=2),
    ]

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001", chunks=chunks
    )

    assert contexts["chunk_002"].nearby_chunk_ids == ("chunk_001", "chunk_003")


def test_chunks_in_different_sections_are_not_nearby() -> None:
    chunks = [
        make_chunk("chunk_001", chunk_index=1, section_id="section_a"),
        make_chunk("chunk_002", chunk_index=2, section_id="section_b"),
    ]

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001", chunks=chunks
    )

    assert contexts["chunk_001"].nearby_chunk_ids == ()
    assert contexts["chunk_002"].nearby_chunk_ids == ()


def test_chunk_with_no_section_id_gets_empty_nearby_chunk_ids() -> None:
    chunks = [make_chunk("chunk_001", chunk_index=1, section_id=None)]

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001", chunks=chunks
    )

    assert contexts["chunk_001"].nearby_chunk_ids == ()


def test_parent_section_id_resolved_from_sections_map() -> None:
    chunks = [make_chunk("chunk_001", chunk_index=1)]
    section = DocumentSection(
        section_id="section_001",
        document_id="document_001",
        title="Maintenance",
        parent_section_id="section_root",
    )

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001",
        chunks=chunks,
        sections={"section_001": section},
    )

    assert contexts["chunk_001"].parent_section_id == "section_root"


def test_parent_section_id_is_none_when_sections_not_provided() -> None:
    chunks = [make_chunk("chunk_001", chunk_index=1)]

    contexts = SemanticExtractionContextBuilder().build_all(
        document_id="document_001", chunks=chunks
    )

    assert contexts["chunk_001"].parent_section_id is None
