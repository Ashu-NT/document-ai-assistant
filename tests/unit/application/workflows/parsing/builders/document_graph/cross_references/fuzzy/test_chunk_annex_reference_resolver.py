from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_annex_number_index import (
    ChunkAnnexNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_annex_reference_resolver import (
    ChunkAnnexReferenceResolver,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(
    *,
    chunk_id: str,
    content: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
    sequence_number: int = 1,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content=content,
        chunk_type=chunk_type,
        source=SourceLocation(page_start=1, page_end=1),
        sequence_number=sequence_number,
    )


def _resolver() -> ChunkAnnexReferenceResolver:
    return ChunkAnnexReferenceResolver()


def test_resolves_uniquely_when_exactly_one_chunk_mentions_the_label() -> None:
    chunk = make_chunk(chunk_id="a", content="8.2 Annex 2\n\nSensors")
    index = ChunkAnnexNumberIndex([chunk])

    result = _resolver().resolve(target_label="2", index=index)

    assert result.target_chunk_id == "a"
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE
    assert result.confidence_score == 0.75


def test_resolves_ambiguously_and_tie_breaks_when_multiple_chunks_mention_the_label() -> (
    None
):
    listing = make_chunk(
        chunk_id="listing",
        content="8.1 Annex 1\n\nDrawings\n\n8.2 Annex 2\n\nSensors",
        sequence_number=1,
    )
    echo = make_chunk(
        chunk_id="echo",
        content="8.2 Annex 2 (continued)\n\nSensors",
        sequence_number=2,
    )
    index = ChunkAnnexNumberIndex([listing, echo])

    result = _resolver().resolve(target_label="2", index=index)

    assert result.target_chunk_id == "listing"
    assert (
        result.resolution_status == ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS
    )
    assert result.confidence_score == 0.5


def test_returns_unresolved_when_no_chunk_mentions_the_label() -> None:
    chunk = make_chunk(chunk_id="a", content="Nothing annex-related here.")
    index = ChunkAnnexNumberIndex([chunk])

    result = _resolver().resolve(target_label="9", index=index)

    assert result.target_chunk_id is None
    assert result.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED
    assert result.confidence_score == 0.0
