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
from src.shared.exceptions import DatabaseError


class ExtractionWriter:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_extraction_result(self, result: ExtractionResult) -> None:
        try:
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