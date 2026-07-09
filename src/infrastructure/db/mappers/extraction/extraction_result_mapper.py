from src.domain.extraction import ExtractionResult
from src.infrastructure.db.mappers.extraction.extraction_chunk_coverage_mapper import (
    ExtractionChunkCoverageMapper,
)
from src.infrastructure.db.mappers.extraction.contact_point_mapper import (
    ContactPointMapper,
)
from src.infrastructure.db.mappers.extraction.equipment_info_mapper import (
    EquipmentInfoMapper,
)
from src.infrastructure.db.mappers.extraction.maintenance_interval_mapper import (
    MaintenanceIntervalMapper,
)
from src.infrastructure.db.mappers.extraction.maintenance_task_mapper import (
    MaintenanceTaskMapper,
)
from src.infrastructure.db.mappers.extraction.manufacturer_mapper import (
    ManufacturerMapper,
)
from src.infrastructure.db.mappers.extraction.procedure_mapper import (
    ProcedureMapper,
)
from src.infrastructure.db.mappers.extraction.safety_warning_mapper import (
    SafetyWarningMapper,
)
from src.infrastructure.db.mappers.extraction.spare_part_mapper import (
    SparePartMapper,
)
from src.infrastructure.db.mappers.extraction.specification_mapper import (
    SpecificationMapper,
)
from src.infrastructure.db.mappers.extraction.supplier_mapper import (
    SupplierMapper,
)
from src.infrastructure.db.mappers.extraction.troubleshooting_entry_mapper import (
    TroubleshootingEntryMapper,
)
from src.infrastructure.db.orm_models import (
    ContactPointORM,
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


class ExtractionResultMapper:
    @staticmethod
    def to_orm(result: ExtractionResult) -> ExtractionResultORM:
        return ExtractionResultORM(
            id=result.extraction_id,
            document_id=result.document_id,
            confidence_score=result.confidence_score,
            requires_human_review=result.requires_human_review,
            source_chunk_ids_json=ExtractionChunkCoverageMapper.dump_chunk_ids(
                result.source_chunk_ids
            ),
            attempted_chunk_ids_json=ExtractionChunkCoverageMapper.dump_chunk_ids(
                result.attempted_chunk_ids
            ),
            unresolved_chunk_ids_json=ExtractionChunkCoverageMapper.dump_chunk_ids(
                result.unresolved_chunk_ids
            ),
            created_at=result.audit.created_at,
        )

    @staticmethod
    def to_domain(
        orm: ExtractionResultORM,
        task_rows: list[MaintenanceTaskORM] | None = None,
        spare_part_rows: list[SparePartORM] | None = None,
        equipment_rows: list[EquipmentInfoORM] | None = None,
        manufacturer_rows: list[ManufacturerORM] | None = None,
        supplier_rows: list[SupplierORM] | None = None,
        contact_point_rows: list[ContactPointORM] | None = None,
        procedure_rows: list[ProcedureORM] | None = None,
        specification_rows: list[SpecificationORM] | None = None,
        safety_warning_rows: list[SafetyWarningORM] | None = None,
        maintenance_interval_rows: list[MaintenanceIntervalORM] | None = None,
        troubleshooting_entry_rows: list[TroubleshootingEntryORM] | None = None,
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
            suppliers=[
                SupplierMapper.to_domain(row)
                for row in supplier_rows or []
            ],
            contact_points=[
                ContactPointMapper.to_domain(row)
                for row in contact_point_rows or []
            ],
            procedures=[
                ProcedureMapper.to_domain(row)
                for row in procedure_rows or []
            ],
            specifications=[
                SpecificationMapper.to_domain(row)
                for row in specification_rows or []
            ],
            safety_warnings=[
                SafetyWarningMapper.to_domain(row)
                for row in safety_warning_rows or []
            ],
            maintenance_intervals=[
                MaintenanceIntervalMapper.to_domain(row)
                for row in maintenance_interval_rows or []
            ],
            troubleshooting_entries=[
                TroubleshootingEntryMapper.to_domain(row)
                for row in troubleshooting_entry_rows or []
            ],
            source_chunk_ids=ExtractionChunkCoverageMapper.load_chunk_ids(
                orm.source_chunk_ids_json
            ),
            attempted_chunk_ids=ExtractionChunkCoverageMapper.load_chunk_ids(
                orm.attempted_chunk_ids_json
            ),
            unresolved_chunk_ids=ExtractionChunkCoverageMapper.load_chunk_ids(
                orm.unresolved_chunk_ids_json
            ),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )
