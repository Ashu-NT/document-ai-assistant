from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import ExtractionResult
from src.infrastructure.db.mappers import ExtractionResultMapper
from src.infrastructure.db.orm_models import (
    EquipmentInfoORM,
    ExtractionResultORM,
    MaintenanceTaskORM,
    ManufacturerORM,
    SparePartORM,
)
from src.shared.exceptions import DatabaseError


class ExtractionReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_extraction_result(
        self,
        extraction_id: str,
    ) -> ExtractionResult | None:
        try:
            result_row = self.session.get(ExtractionResultORM, extraction_id)

            if result_row is None:
                return None

            task_rows = self.session.execute(
                select(MaintenanceTaskORM).where(
                    MaintenanceTaskORM.extraction_id == extraction_id
                )
            ).scalars().all()

            spare_part_rows = self.session.execute(
                select(SparePartORM).where(
                    SparePartORM.extraction_id == extraction_id
                )
            ).scalars().all()

            equipment_rows = self.session.execute(
                select(EquipmentInfoORM).where(
                    EquipmentInfoORM.extraction_id == extraction_id
                )
            ).scalars().all()

            manufacturer_rows = self.session.execute(
                select(ManufacturerORM).where(
                    ManufacturerORM.extraction_id == extraction_id
                )
            ).scalars().all()

            return ExtractionResultMapper.to_domain(
                result_row,
                task_rows=task_rows,
                spare_part_rows=spare_part_rows,
                equipment_rows=equipment_rows,
                manufacturer_rows=manufacturer_rows,
            )

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load extraction result.",
                details={"extraction_id": extraction_id},
            ) from exc