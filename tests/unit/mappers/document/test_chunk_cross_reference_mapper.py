from src.infrastructure.db.mappers import ChunkCrossReferenceMapper


def test_chunk_cross_reference_mapper_round_trip(sample_chunk_cross_reference) -> None:
    orm = ChunkCrossReferenceMapper.to_orm(sample_chunk_cross_reference)
    domain = ChunkCrossReferenceMapper.to_domain(orm)

    assert domain.cross_reference_id == sample_chunk_cross_reference.cross_reference_id
    assert domain.document_id == sample_chunk_cross_reference.document_id
    assert domain.source_chunk_id == sample_chunk_cross_reference.source_chunk_id
    assert domain.target_chunk_id == sample_chunk_cross_reference.target_chunk_id
    assert domain.reference_type == sample_chunk_cross_reference.reference_type
    assert domain.matched_text == sample_chunk_cross_reference.matched_text
    assert domain.target_page == sample_chunk_cross_reference.target_page
    assert domain.resolution_status == sample_chunk_cross_reference.resolution_status
    assert domain.confidence_score == sample_chunk_cross_reference.confidence_score


def test_chunk_cross_reference_mapper_round_trip_for_unresolved_section_reference() -> (
    None
):
    from src.domain.document.entities import (
        ChunkCrossReference,
        ChunkCrossReferenceResolutionStatus,
        ChunkCrossReferenceType,
    )

    section_reference = ChunkCrossReference(
        cross_reference_id="xref_002",
        document_id="doc_001",
        source_chunk_id="chunk_001",
        reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
        matched_text="chap. 8.9",
        target_section_label="8.9",
        target_page=None,
        target_chunk_id=None,
        resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
        confidence_score=0.0,
    )

    orm = ChunkCrossReferenceMapper.to_orm(section_reference)
    domain = ChunkCrossReferenceMapper.to_domain(orm)

    assert domain.reference_type == ChunkCrossReferenceType.SECTION_REFERENCE
    assert domain.target_section_label == "8.9"
    assert domain.target_page is None
    assert domain.target_chunk_id is None
    assert domain.resolution_status == ChunkCrossReferenceResolutionStatus.UNRESOLVED
