from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import ExtractionResult
from src.infrastructure.db.mappers import (
    EquipmentInfoMapper,
    ExtractionResultMapper,
    MaintenanceTaskMapper,
    ManufacturerMapper,
    SparePartMapper,
)
from src.infrastructure.db.orm_models import (
    EquipmentInfoORM,
    ExtractionResultORM,
    ManufacturerORM,
    MaintenanceTaskORM,
    SparePartORM,
)
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

    def _insert_extraction_result(self, result: ExtractionResult) -> None:
        self.session.merge(ExtractionResultMapper.to_orm(result))

        for task in result.maintenance_tasks:
            self.session.merge(
                MaintenanceTaskMapper.to_orm(
                    task,
                    extraction_id=result.extraction_id,
                )
            )

        for spare_part in result.spare_parts:
            self.session.merge(
                SparePartMapper.to_orm(
                    spare_part,
                    extraction_id=result.extraction_id,
                )
            )

        for equipment in result.equipment:
            self.session.merge(
                EquipmentInfoMapper.to_orm(
                    equipment,
                    extraction_id=result.extraction_id,
                )
            )

        for manufacturer in result.manufacturers:
            self.session.merge(
                ManufacturerMapper.to_orm(
                    manufacturer,
                    extraction_id=result.extraction_id,
                )
            )

    def _delete_extraction_result(self, document_id: str) -> None:
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
            delete(ExtractionResultORM).where(
                ExtractionResultORM.document_id == document_id
            )
        )