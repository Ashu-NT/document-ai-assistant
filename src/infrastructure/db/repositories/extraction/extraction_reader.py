from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.extraction import ExtractionResult
from src.infrastructure.db.mappers import ExtractionResultMapper
from src.infrastructure.db.orm_models import (
    EquipmentInfoORM,
    ExtractionResultORM,
    MaintenanceIntervalORM,
    MaintenanceTaskORM,
    ManufacturerORM,
    ProcedureORM,
    SafetyWarningORM,
    SparePartORM,
    SpecificationORM,
    SupplierORM,
    TroubleshootingEntryORM,
)
from src.shared.exceptions import DatabaseError


class ExtractionReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def has_extraction_result(self, document_id: str) -> bool:
        try:
            extraction_id = self.session.execute(
                select(ExtractionResultORM.id)
                .where(ExtractionResultORM.document_id == document_id)
                .limit(1)
            ).scalar()

            return extraction_id is not None

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to check for an existing extraction result.",
                details={"document_id": document_id},
            ) from exc

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

            supplier_rows = self.session.execute(
                select(SupplierORM).where(
                    SupplierORM.extraction_id == extraction_id
                )
            ).scalars().all()

            procedure_rows = self.session.execute(
                select(ProcedureORM).where(
                    ProcedureORM.extraction_id == extraction_id
                )
            ).scalars().all()

            specification_rows = self.session.execute(
                select(SpecificationORM).where(
                    SpecificationORM.extraction_id == extraction_id
                )
            ).scalars().all()

            safety_warning_rows = self.session.execute(
                select(SafetyWarningORM).where(
                    SafetyWarningORM.extraction_id == extraction_id
                )
            ).scalars().all()

            maintenance_interval_rows = self.session.execute(
                select(MaintenanceIntervalORM).where(
                    MaintenanceIntervalORM.extraction_id == extraction_id
                )
            ).scalars().all()

            troubleshooting_entry_rows = self.session.execute(
                select(TroubleshootingEntryORM).where(
                    TroubleshootingEntryORM.extraction_id == extraction_id
                )
            ).scalars().all()

            return ExtractionResultMapper.to_domain(
                result_row,
                task_rows=task_rows,
                spare_part_rows=spare_part_rows,
                equipment_rows=equipment_rows,
                manufacturer_rows=manufacturer_rows,
                supplier_rows=supplier_rows,
                procedure_rows=procedure_rows,
                specification_rows=specification_rows,
                safety_warning_rows=safety_warning_rows,
                maintenance_interval_rows=maintenance_interval_rows,
                troubleshooting_entry_rows=troubleshooting_entry_rows,
            )

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load extraction result.",
                details={"extraction_id": extraction_id},
            ) from exc

    def get_document_extraction_result(
        self,
        document_id: str,
    ) -> ExtractionResult | None:
        try:
            extraction_id = self.session.execute(
                select(ExtractionResultORM.id)
                .where(ExtractionResultORM.document_id == document_id)
                .order_by(desc(ExtractionResultORM.created_at))
                .limit(1)
            ).scalar()
            if extraction_id is None:
                return None
            return self.get_extraction_result(extraction_id)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load extraction result for document.",
                details={"document_id": document_id},
            ) from exc
