from src.domain.extraction import ExtractionResult
from src.infrastructure.db.mappers.extraction.equipment_info_mapper import (
    EquipmentInfoMapper,
)
from src.infrastructure.db.mappers.extraction.maintenance_task_mapper import (
    MaintenanceTaskMapper,
)
from src.infrastructure.db.mappers.extraction.manufacturer_mapper import (
    ManufacturerMapper,
)
from src.infrastructure.db.mappers.extraction.spare_part_mapper import (
    SparePartMapper,
)
from src.infrastructure.db.orm_models import (
    EquipmentInfoORM,
    ExtractionResultORM,
    MaintenanceTaskORM,
    ManufacturerORM,
    SparePartORM,
)


class ExtractionResultMapper:
    @staticmethod
    def to_orm(result: ExtractionResult) -> ExtractionResultORM:
        return ExtractionResultORM(
            id=result.extraction_id,
            document_id=result.document_id,
            confidence_score=result.confidence_score,
            requires_human_review=result.requires_human_review,
            created_at=result.audit.created_at,
        )

    @staticmethod
    def to_domain(
        orm: ExtractionResultORM,
        task_rows: list[MaintenanceTaskORM] | None = None,
        spare_part_rows: list[SparePartORM] | None = None,
        equipment_rows: list[EquipmentInfoORM] | None = None,
        manufacturer_rows: list[ManufacturerORM] | None = None,
    ) -> ExtractionResult:
        return ExtractionResult(
            extraction_id=orm.id,
            document_id=orm.document_id,
            maintenance_tasks=[
                MaintenanceTaskMapper.to_domain(row)
                for row in task_rows or []
            ],
            spare_parts=[
                SparePartMapper.to_domain(row)
                for row in spare_part_rows or []
            ],
            equipment=[
                EquipmentInfoMapper.to_domain(row)
                for row in equipment_rows or []
            ],
            manufacturers=[
                ManufacturerMapper.to_domain(row)
                for row in manufacturer_rows or []
            ],
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )