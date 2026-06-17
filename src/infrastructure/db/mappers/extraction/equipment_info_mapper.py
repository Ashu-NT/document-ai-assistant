from src.domain.extraction import EquipmentInfo
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import EquipmentInfoORM


class EquipmentInfoMapper:
    @staticmethod
    def to_orm(
        equipment: EquipmentInfo,
        extraction_id: str | None = None,
    ) -> EquipmentInfoORM:
        return EquipmentInfoORM(
            id=equipment.equipment_id,
            extraction_id=extraction_id,
            document_id=equipment.document_id,
            name=equipment.name,
            model_number=equipment.model_number,
            serial_number=equipment.serial_number,
            manufacturer_name=equipment.manufacturer_name,
            source_chunk_id=equipment.source_chunk_id,
            page_start=equipment.source.page_start,
            page_end=equipment.source.page_end,
            confidence_score=equipment.confidence_score,
            requires_human_review=equipment.requires_human_review,
            created_at=equipment.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: EquipmentInfoORM) -> EquipmentInfo:
        return EquipmentInfo(
            equipment_id=orm.id,
            document_id=orm.document_id,
            name=orm.name,
            model_number=orm.model_number,
            serial_number=orm.serial_number,
            manufacturer_name=orm.manufacturer_name,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )