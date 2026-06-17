from src.domain.extraction import MaintenanceTask
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import MaintenanceTaskORM


class MaintenanceTaskMapper:
    @staticmethod
    def to_orm(
        task: MaintenanceTask,
        extraction_id: str | None = None,
    ) -> MaintenanceTaskORM:
        return MaintenanceTaskORM(
            id=task.task_id,
            extraction_id=extraction_id,
            document_id=task.document_id,
            title=task.title,
            description=task.description,
            interval=task.interval,
            component_name=task.component_name,
            equipment_id=task.equipment_id,
            source_chunk_id=task.source_chunk_id,
            page_start=task.source.page_start,
            page_end=task.source.page_end,
            confidence_score=task.confidence_score,
            requires_human_review=task.requires_human_review,
            created_at=task.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: MaintenanceTaskORM) -> MaintenanceTask:
        return MaintenanceTask(
            task_id=orm.id,
            document_id=orm.document_id,
            title=orm.title,
            description=orm.description,
            interval=orm.interval,
            component_name=orm.component_name,
            equipment_id=orm.equipment_id,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )