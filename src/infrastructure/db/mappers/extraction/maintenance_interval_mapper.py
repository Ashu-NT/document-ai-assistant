from src.domain.extraction import MaintenanceInterval
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
    json_to_source_metadata,
    source_metadata_to_json,
)
from src.infrastructure.db.orm_models import MaintenanceIntervalORM


class MaintenanceIntervalMapper:
    @staticmethod
    def to_orm(
        maintenance_interval: MaintenanceInterval,
        extraction_id: str | None = None,
    ) -> MaintenanceIntervalORM:
        return MaintenanceIntervalORM(
            id=maintenance_interval.maintenance_interval_id,
            extraction_id=extraction_id,
            document_id=maintenance_interval.document_id,
            interval=maintenance_interval.interval,
            component_name=maintenance_interval.component_name,
            maintenance_task_id=maintenance_interval.maintenance_task_id,
            source_chunk_id=maintenance_interval.source_chunk_id,
            page_start=maintenance_interval.source.page_start,
            page_end=maintenance_interval.source.page_end,
            source_metadata_json=source_metadata_to_json(
                maintenance_interval.source_metadata
            ),
            confidence_score=maintenance_interval.confidence_score,
            requires_human_review=maintenance_interval.requires_human_review,
            created_at=maintenance_interval.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: MaintenanceIntervalORM) -> MaintenanceInterval:
        return MaintenanceInterval(
            maintenance_interval_id=orm.id,
            document_id=orm.document_id,
            interval=orm.interval,
            component_name=orm.component_name,
            maintenance_task_id=orm.maintenance_task_id,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            source_metadata=json_to_source_metadata(orm.source_metadata_json),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )
