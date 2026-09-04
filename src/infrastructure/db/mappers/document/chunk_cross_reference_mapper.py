from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    CrossReferenceReconciliationOutcome,
)
from src.infrastructure.db.mappers.common.pdf_link_provenance_mapper import (
    json_to_pdf_link_provenance,
    pdf_link_provenance_to_json,
)
from src.infrastructure.db.orm_models import ChunkCrossReferenceORM


class ChunkCrossReferenceMapper:
    @staticmethod
    def to_orm(cross_reference: ChunkCrossReference) -> ChunkCrossReferenceORM:
        return ChunkCrossReferenceORM(
            id=cross_reference.cross_reference_id,
            document_id=cross_reference.document_id,
            source_chunk_id=cross_reference.source_chunk_id,
            target_chunk_id=cross_reference.target_chunk_id,
            reference_type=cross_reference.reference_type.value,
            matched_text=cross_reference.matched_text,
            target_page=cross_reference.target_page,
            target_section_label=cross_reference.target_section_label,
            target_asset_label=cross_reference.target_asset_label,
            resolution_status=cross_reference.resolution_status.value,
            confidence_score=cross_reference.confidence_score,
            link_provenance_json=pdf_link_provenance_to_json(
                cross_reference.link_provenance
            ),
            reconciliation_outcome=(
                cross_reference.reconciliation_outcome.value
                if cross_reference.reconciliation_outcome is not None
                else None
            ),
            created_at=cross_reference.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: ChunkCrossReferenceORM) -> ChunkCrossReference:
        return ChunkCrossReference(
            cross_reference_id=orm.id,
            document_id=orm.document_id,
            source_chunk_id=orm.source_chunk_id,
            target_chunk_id=orm.target_chunk_id,
            reference_type=ChunkCrossReferenceType(orm.reference_type),
            matched_text=orm.matched_text,
            target_page=orm.target_page,
            target_section_label=orm.target_section_label,
            target_asset_label=orm.target_asset_label,
            resolution_status=ChunkCrossReferenceResolutionStatus(orm.resolution_status),
            confidence_score=orm.confidence_score,
            link_provenance=json_to_pdf_link_provenance(orm.link_provenance_json),
            reconciliation_outcome=(
                CrossReferenceReconciliationOutcome(orm.reconciliation_outcome)
                if orm.reconciliation_outcome is not None
                else None
            ),
        )
