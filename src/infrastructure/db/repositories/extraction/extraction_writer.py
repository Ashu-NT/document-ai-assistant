from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import ExtractionResult, SemanticRelationship
from src.infrastructure.db.mappers import (
    ContactPointMapper,
    EquipmentInfoMapper,
    ExtractionResultMapper,
    MaintenanceIntervalMapper,
    MaintenanceTaskMapper,
    ManufacturerMapper,
    ProcedureMapper,
    SafetyWarningMapper,
    SemanticRelationshipMapper,
    SparePartMapper,
    SpecificationMapper,
    SupplierMapper,
    TroubleshootingEntryMapper,
)
from src.infrastructure.db.orm_models import (
    ContactPointORM,
    EquipmentInfoORM,
    ExtractionResultORM,
    MaintenanceIntervalORM,
    ManufacturerORM,
    MaintenanceTaskORM,
    ProcedureORM,
    SafetyWarningORM,
    SemanticRelationshipORM,
    SparePartORM,
    SpecificationORM,
    SupplierORM,
    TroubleshootingEntryORM,
)
from src.infrastructure.db.repositories.common import bulk_merge
from src.shared.exceptions import DatabaseError


class ExtractionWriter:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_extraction_result(self, result: ExtractionResult) -> None:
        try:
            self._insert_extraction_result(result)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save extraction result.",
                details={
                    "extraction_id": result.extraction_id,
                    "document_id": result.document_id,
                    "task_count": len(result.maintenance_tasks),
                    "spare_part_count": len(result.spare_parts),
                },
            ) from exc

    def replace_extraction_result(self, result: ExtractionResult) -> None:
        """Atomically replace all extraction-family rows for a document.

        Unlike `save_extraction_result` (an insert keyed by a fresh
        `extraction_id` every run), this deletes the document's prior
        extraction rows first so re-extraction (reingest) does not leave
        orphaned duplicates behind, mirroring
        `DocumentWriter.replace_document_chunk_artifacts`.
        """
        try:
            self._delete_extraction_result(result.document_id)
            self._insert_extraction_result(result)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to replace extraction result.",
                details={
                    "extraction_id": result.extraction_id,
                    "document_id": result.document_id,
                    "task_count": len(result.maintenance_tasks),
                    "spare_part_count": len(result.spare_parts),
                },
            ) from exc

    def delete_by_document(self, document_id: str) -> None:
        try:
            self._delete_extraction_result(document_id)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to delete extraction result.",
                details={"document_id": document_id},
            ) from exc

    def replace_semantic_relationships(
        self,
        document_id: str,
        relationships: list[SemanticRelationship],
    ) -> None:
        """Replace all semantic relationships for a document.

        Relationships are derived post-hoc from already-persisted extraction
        entities (by `SemanticLinkingWorkflow`), not part of the LLM
        extraction cascade itself, so they are keyed by `document_id` alone
        and can be recomputed/re-run independently of extraction.
        """
        try:
            self.session.execute(
                delete(SemanticRelationshipORM).where(
                    SemanticRelationshipORM.document_id == document_id
                )
            )
            bulk_merge(
                self.session,
                SemanticRelationshipORM,
                [
                    SemanticRelationshipMapper.to_orm(relationship)
                    for relationship in relationships
                ],
            )
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to replace semantic relationships.",
                details={
                    "document_id": document_id,
                    "relationship_count": len(relationships),
                },
            ) from exc

    def _insert_extraction_result(self, result: ExtractionResult) -> None:
        # Explicit flush()es: none of these ORM classes have a relationship()
        # declared toward ExtractionResultORM/EquipmentInfoORM/
        # MaintenanceTaskORM (only plain FK columns), so SQLAlchemy's
        # automatic flush-time insert ordering cannot topologically sort
        # them within a single flush -- see the identical fix and
        # explanation in DocumentWriter._merge_document_structure.
        self.session.merge(ExtractionResultMapper.to_orm(result))
        self.session.flush()

        bulk_merge(
            self.session,
            MaintenanceTaskORM,
            [
                MaintenanceTaskMapper.to_orm(task, extraction_id=result.extraction_id)
                for task in result.maintenance_tasks
            ],
        )
        bulk_merge(
            self.session,
            SparePartORM,
            [
                SparePartMapper.to_orm(spare_part, extraction_id=result.extraction_id)
                for spare_part in result.spare_parts
            ],
        )
        bulk_merge(
            self.session,
            EquipmentInfoORM,
            [
                EquipmentInfoMapper.to_orm(equipment, extraction_id=result.extraction_id)
                for equipment in result.equipment
            ],
        )
        bulk_merge(
            self.session,
            ManufacturerORM,
            [
                ManufacturerMapper.to_orm(manufacturer, extraction_id=result.extraction_id)
                for manufacturer in result.manufacturers
            ],
        )
        bulk_merge(
            self.session,
            SupplierORM,
            [
                SupplierMapper.to_orm(supplier, extraction_id=result.extraction_id)
                for supplier in result.suppliers
            ],
        )
        bulk_merge(
            self.session,
            ContactPointORM,
            [
                ContactPointMapper.to_orm(
                    contact_point, extraction_id=result.extraction_id
                )
                for contact_point in result.contact_points
            ],
        )
        # equipment_info and maintenance_tasks must be flushed before
        # procedures/troubleshooting_entries/maintenance_intervals below,
        # which reference them via equipment_id/maintenance_task_id.
        self.session.flush()

        bulk_merge(
            self.session,
            ProcedureORM,
            [
                ProcedureMapper.to_orm(procedure, extraction_id=result.extraction_id)
                for procedure in result.procedures
            ],
        )
        bulk_merge(
            self.session,
            SpecificationORM,
            [
                SpecificationMapper.to_orm(specification, extraction_id=result.extraction_id)
                for specification in result.specifications
            ],
        )
        bulk_merge(
            self.session,
            SafetyWarningORM,
            [
                SafetyWarningMapper.to_orm(safety_warning, extraction_id=result.extraction_id)
                for safety_warning in result.safety_warnings
            ],
        )
        bulk_merge(
            self.session,
            MaintenanceIntervalORM,
            [
                MaintenanceIntervalMapper.to_orm(
                    maintenance_interval, extraction_id=result.extraction_id
                )
                for maintenance_interval in result.maintenance_intervals
            ],
        )
        bulk_merge(
            self.session,
            TroubleshootingEntryORM,
            [
                TroubleshootingEntryMapper.to_orm(
                    troubleshooting_entry, extraction_id=result.extraction_id
                )
                for troubleshooting_entry in result.troubleshooting_entries
            ],
        )

    def _delete_extraction_result(self, document_id: str) -> None:
        self.session.execute(
            delete(MaintenanceIntervalORM).where(
                MaintenanceIntervalORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(SafetyWarningORM).where(
                SafetyWarningORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(SpecificationORM).where(
                SpecificationORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(TroubleshootingEntryORM).where(
                TroubleshootingEntryORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(ProcedureORM).where(
                ProcedureORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(MaintenanceTaskORM).where(
                MaintenanceTaskORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(SparePartORM).where(SparePartORM.document_id == document_id)
        )
        self.session.execute(
            delete(EquipmentInfoORM).where(
                EquipmentInfoORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(ManufacturerORM).where(
                ManufacturerORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(SupplierORM).where(
                SupplierORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(ContactPointORM).where(
                ContactPointORM.document_id == document_id
            )
        )
        self.session.execute(
            delete(ExtractionResultORM).where(
                ExtractionResultORM.document_id == document_id
            )
        )
