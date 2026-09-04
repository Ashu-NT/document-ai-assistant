from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_section_number_index import (
    ChunkSectionNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_section_reference_resolver import (
    ChunkSectionReferenceResolver,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(
    *,
    chunk_id: str,
    section_path: list[str],
    chunk_type: ChunkType = ChunkType.GENERAL,
    sequence_number: int = 1,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content="content",
        chunk_type=chunk_type,
        section_path=section_path,
        source=SourceLocation(page_start=1, page_end=1),
        sequence_number=sequence_number,
    )


def _resolver() -> ChunkSectionReferenceResolver:
    return ChunkSectionReferenceResolver()


def test_resolves_uniquely_when_exactly_one_chunk_matches_the_section() -> None:
    chunk = make_chunk(chunk_id="a", section_path=["6.3 Lubrication System"])
    index = ChunkSectionNumberIndex([chunk])

    result = _resolver().resolve(target_section_label="6.3", index=index)

    assert result.target_chunk_id == "a"
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE
    assert result.confidence_score == 0.85


def test_prefers_procedure_like_chunk_when_multiple_chunks_share_the_section() -> None:
    overview = make_chunk(
        chunk_id="overview",
        section_path=["6.3 Lubrication System"],
        chunk_type=ChunkType.OVERVIEW,
        sequence_number=1,
    )
    procedure = make_chunk(
        chunk_id="procedure",
        section_path=["6.3 Lubrication System"],
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        sequence_number=2,
    )
    index = ChunkSectionNumberIndex([overview, procedure])

    result = _resolver().resolve(target_section_label="6.3", index=index)

    assert result.target_chunk_id == "procedure"
    assert (
        result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    )
    assert result.confidence_score == 0.55


def test_falls_back_to_earliest_descendant_subsection_when_section_itself_is_not_chunked() -> (
    None
):
    later = make_chunk(
        chunk_id="later",
        section_path=["6.3.2 Oil change"],
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        sequence_number=5,
    )
    earlier = make_chunk(
        chunk_id="earlier",
        section_path=["6.3.1 Filter check"],
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        sequence_number=2,
    )
    index = ChunkSectionNumberIndex([later, earlier])

    result = _resolver().resolve(target_section_label="6.3", index=index)

    assert result.target_chunk_id == "earlier"
    assert (
        result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    )
    assert result.confidence_score == 0.5


def test_returns_unresolved_when_no_section_or_descendant_matches() -> None:
    chunk = make_chunk(chunk_id="a", section_path=["7 Unrelated Section"])
    index = ChunkSectionNumberIndex([chunk])

    result = _resolver().resolve(target_section_label="6.3", index=index)

    assert result.target_chunk_id is None
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED
    assert result.confidence_score == 0.0


def test_prefers_exact_section_match_over_a_descendant_subsection() -> None:
    exact = make_chunk(
        chunk_id="exact",
        section_path=["6.3 Lubrication System"],
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
    )
    descendant = make_chunk(
        chunk_id="descendant",
        section_path=["6.3.1 Filter check"],
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
    )
    index = ChunkSectionNumberIndex([exact, descendant])

    result = _resolver().resolve(target_section_label="6.3", index=index)

    assert result.target_chunk_id == "exact"
