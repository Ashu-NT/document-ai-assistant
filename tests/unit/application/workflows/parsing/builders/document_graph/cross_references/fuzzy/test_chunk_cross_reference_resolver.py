from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_resolver import (
    ChunkCrossReferenceResolver,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(
    *,
    chunk_id: str,
    page_start: int | None,
    page_end: int | None = None,
    chunk_type: ChunkType = ChunkType.GENERAL,
    sequence_number: int = 1,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content="content",
        chunk_type=chunk_type,
        source=SourceLocation(page_start=page_start, page_end=page_end or page_start),
        sequence_number=sequence_number,
    )


def _resolver() -> ChunkCrossReferenceResolver:
    return ChunkCrossReferenceResolver()


def test_resolves_uniquely_when_exactly_one_candidate_covers_the_page() -> None:
    chunks = [
        make_chunk(chunk_id="c1", page_start=5),
        make_chunk(chunk_id="c2", page_start=42),
        make_chunk(chunk_id="c3", page_start=50),
    ]

    result = _resolver().resolve(target_page=42, chunks=chunks)

    assert result.target_chunk_id == "c2"
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE
    assert result.confidence_score == 0.9


def test_resolves_uniquely_across_a_multi_page_chunk_span() -> None:
    chunks = [make_chunk(chunk_id="c1", page_start=40, page_end=45)]

    result = _resolver().resolve(target_page=42, chunks=chunks)

    assert result.target_chunk_id == "c1"
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE


def test_returns_unresolved_when_no_chunk_covers_the_target_page() -> None:
    chunks = [make_chunk(chunk_id="c1", page_start=5)]

    result = _resolver().resolve(target_page=999, chunks=chunks)

    assert result.target_chunk_id is None
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED
    assert result.confidence_score == 0.0


def test_returns_unresolved_when_no_chunk_has_a_page_at_all() -> None:
    chunks = [make_chunk(chunk_id="c1", page_start=None, page_end=None)]

    result = _resolver().resolve(target_page=1, chunks=chunks)

    assert result.target_chunk_id is None
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED


def test_prefers_procedure_like_chunk_type_when_multiple_candidates_share_a_page() -> (
    None
):
    chunks = [
        make_chunk(chunk_id="general", page_start=42, chunk_type=ChunkType.GENERAL),
        make_chunk(
            chunk_id="procedure",
            page_start=42,
            chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        ),
    ]

    result = _resolver().resolve(target_page=42, chunks=chunks)

    assert result.target_chunk_id == "procedure"
    assert (
        result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    )
    assert result.confidence_score == 0.6


def test_prefers_exact_page_start_match_over_a_merely_spanning_chunk() -> None:
    chunks = [
        make_chunk(
            chunk_id="spanning",
            page_start=40,
            page_end=45,
            chunk_type=ChunkType.TROUBLESHOOTING,
        ),
        make_chunk(
            chunk_id="exact",
            page_start=42,
            chunk_type=ChunkType.TROUBLESHOOTING,
        ),
    ]

    result = _resolver().resolve(target_page=42, chunks=chunks)

    assert result.target_chunk_id == "exact"


def test_prefers_earliest_sequence_number_as_final_tie_break() -> None:
    chunks = [
        make_chunk(
            chunk_id="second",
            page_start=42,
            chunk_type=ChunkType.OPERATION_INSTRUCTION,
            sequence_number=5,
        ),
        make_chunk(
            chunk_id="first",
            page_start=42,
            chunk_type=ChunkType.OPERATION_INSTRUCTION,
            sequence_number=2,
        ),
    ]

    result = _resolver().resolve(target_page=42, chunks=chunks)

    assert result.target_chunk_id == "first"


def test_falls_back_to_all_candidates_when_none_are_procedure_like() -> None:
    chunks = [
        make_chunk(
            chunk_id="overview",
            page_start=42,
            chunk_type=ChunkType.OVERVIEW,
            sequence_number=1,
        ),
        make_chunk(
            chunk_id="general",
            page_start=42,
            chunk_type=ChunkType.GENERAL,
            sequence_number=2,
        ),
    ]

    result = _resolver().resolve(target_page=42, chunks=chunks)

    assert result.target_chunk_id == "overview"
    assert (
        result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    )
