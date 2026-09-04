from src.domain.document.entities import (
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    CrossReferenceEvidence,
    CrossReferenceReconciliationOutcome,
)
from src.infrastructure.db.mappers.common.pdf_link_provenance_mapper import (
    json_to_pdf_link_provenance,
    pdf_link_provenance_to_json,
)
from src.infrastructure.db.orm_models import CrossReferenceEvidenceORM


class CrossReferenceEvidenceMapper:
    """Insert-and-read only - CrossReferenceEvidence is append-only within a
    document's lifecycle, never updated after insert (see
    outputs/architecture/pdf_link_cross_reference_plan.md §7)."""

    @staticmethod
    def to_orm(evidence: CrossReferenceEvidence) -> CrossReferenceEvidenceORM:
        return CrossReferenceEvidenceORM(
            id=evidence.evidence_id,
            document_id=evidence.document_id,
            source_chunk_id=evidence.source_chunk_id,
            reference_type=evidence.reference_type.value,
            matched_text=evidence.matched_text,
            target_page=evidence.target_page,
            target_section_label=evidence.target_section_label,
            target_chunk_id=evidence.target_chunk_id,
            resolution_status=evidence.resolution_status.value,
            confidence_score=evidence.confidence_score,
            link_provenance_json=pdf_link_provenance_to_json(evidence.link_provenance),
            reconciliation_outcome=(
                evidence.reconciliation_outcome.value
                if evidence.reconciliation_outcome is not None
                else None
            ),
            reconciliation_group_id=evidence.reconciliation_group_id,
            canonical_cross_reference_id=evidence.canonical_cross_reference_id,
            created_at=evidence.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: CrossReferenceEvidenceORM) -> CrossReferenceEvidence:
        return CrossReferenceEvidence(
            evidence_id=orm.id,
            document_id=orm.document_id,
            source_chunk_id=orm.source_chunk_id,
            reference_type=ChunkCrossReferenceType(orm.reference_type),
            matched_text=orm.matched_text,
            target_page=orm.target_page,
            target_section_label=orm.target_section_label,
            target_chunk_id=orm.target_chunk_id,
            resolution_status=ChunkCrossReferenceResolutionStatus(
                orm.resolution_status
            ),
            confidence_score=orm.confidence_score,
            link_provenance=json_to_pdf_link_provenance(orm.link_provenance_json),
            reconciliation_outcome=(
                CrossReferenceReconciliationOutcome(orm.reconciliation_outcome)
                if orm.reconciliation_outcome is not None
                else None
            ),
            reconciliation_group_id=orm.reconciliation_group_id,
            canonical_cross_reference_id=orm.canonical_cross_reference_id,
        )


__all__ = ["CrossReferenceEvidenceMapper"]
