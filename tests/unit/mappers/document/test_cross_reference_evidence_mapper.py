from src.domain.common import BoundingBox
from src.domain.document.entities import (
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    CrossReferenceEvidence,
    CrossReferenceReconciliationOutcome,
    PdfLinkProvenance,
)
from src.infrastructure.db.mappers import CrossReferenceEvidenceMapper


def test_cross_reference_evidence_mapper_round_trip_for_unpromoted_conflict() -> None:
    evidence = CrossReferenceEvidence(
        evidence_id="xref_evidence_001",
        document_id="doc_001",
        source_chunk_id="chunk_001",
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        matched_text="(see page 41)",
        target_page=41,
        target_chunk_id="chunk_003",
        resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
        confidence_score=0.9,
        reconciliation_outcome=CrossReferenceReconciliationOutcome.CONFLICT,
        reconciliation_group_id="xref_evidence_group_001",
        canonical_cross_reference_id=None,
    )

    orm = CrossReferenceEvidenceMapper.to_orm(evidence)
    domain = CrossReferenceEvidenceMapper.to_domain(orm)

    assert domain.evidence_id == "xref_evidence_001"
    assert domain.reference_type == ChunkCrossReferenceType.PAGE_REFERENCE
    assert domain.reconciliation_outcome == CrossReferenceReconciliationOutcome.CONFLICT
    assert domain.reconciliation_group_id == "xref_evidence_group_001"
    assert domain.canonical_cross_reference_id is None


def test_cross_reference_evidence_mapper_round_trip_for_promoted_native_evidence() -> (
    None
):
    evidence = CrossReferenceEvidence(
        evidence_id="xref_evidence_002",
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
        reconciliation_group_id="xref_evidence_group_002",
        canonical_cross_reference_id="xref_canonical_002",
    )

    orm = CrossReferenceEvidenceMapper.to_orm(evidence)
    domain = CrossReferenceEvidenceMapper.to_domain(orm)

    assert domain.link_provenance == evidence.link_provenance
    assert domain.canonical_cross_reference_id == "xref_canonical_002"
    assert domain.reconciliation_outcome == CrossReferenceReconciliationOutcome.CONFIRMED
