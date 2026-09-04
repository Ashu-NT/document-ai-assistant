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


def test_chunk_cross_reference_mapper_round_trip_for_pdf_link_provenance_and_reconciliation_outcome() -> (
    None
):
    from src.domain.common import BoundingBox
    from src.domain.document.entities import (
        ChunkCrossReference,
        ChunkCrossReferenceResolutionStatus,
        ChunkCrossReferenceType,
        CrossReferenceReconciliationOutcome,
        PdfLinkProvenance,
    )

    native_reference = ChunkCrossReference(
        cross_reference_id="xref_003",
        document_id="doc_001",
        source_chunk_id="chunk_001",
        reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
        matched_text="pdf_link_annotation",
        target_page=49,
        target_chunk_id="chunk_002",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
        confidence_score=0.9,
        link_provenance=PdfLinkProvenance(
            source_page=313,
            link_kind="goto",
            source_rect=BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0),
            rect_coordinate_origin="pdf_native_bottom_left",
            source_page_size=(612.0, 792.0),
            source_page_rotation_degrees=0,
            source_page_label="313",
            dest_page_label="41",
        ),
        reconciliation_outcome=CrossReferenceReconciliationOutcome.CONFIRMED,
    )

    orm = ChunkCrossReferenceMapper.to_orm(native_reference)
    domain = ChunkCrossReferenceMapper.to_domain(orm)

    assert domain.reference_type == ChunkCrossReferenceType.PDF_LINK_REFERENCE
    assert domain.reconciliation_outcome == CrossReferenceReconciliationOutcome.CONFIRMED
    assert domain.link_provenance == native_reference.link_provenance
    assert domain.link_provenance.source_page == 313
    assert domain.link_provenance.link_kind == "goto"
    assert domain.link_provenance.dest_page_label == "41"


def test_chunk_cross_reference_mapper_round_trip_with_no_provenance_or_outcome(
    sample_chunk_cross_reference,
) -> None:
    orm = ChunkCrossReferenceMapper.to_orm(sample_chunk_cross_reference)
    domain = ChunkCrossReferenceMapper.to_domain(orm)

    assert domain.link_provenance is None
    assert domain.reconciliation_outcome is None
