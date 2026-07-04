from src.domain.extraction import SafetyWarning
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
    json_to_source_metadata,
    source_metadata_to_json,
)
from src.infrastructure.db.orm_models import SafetyWarningORM


class SafetyWarningMapper:
    @staticmethod
    def to_orm(
        safety_warning: SafetyWarning,
        extraction_id: str | None = None,
    ) -> SafetyWarningORM:
        return SafetyWarningORM(
            id=safety_warning.safety_warning_id,
            extraction_id=extraction_id,
            document_id=safety_warning.document_id,
            warning_type=safety_warning.warning_type,
            message=safety_warning.message,
            component_name=safety_warning.component_name,
            source_chunk_id=safety_warning.source_chunk_id,
            page_start=safety_warning.source.page_start,
            page_end=safety_warning.source.page_end,
            source_metadata_json=source_metadata_to_json(safety_warning.source_metadata),
            confidence_score=safety_warning.confidence_score,
            requires_human_review=safety_warning.requires_human_review,
            created_at=safety_warning.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: SafetyWarningORM) -> SafetyWarning:
        return SafetyWarning(
            safety_warning_id=orm.id,
            document_id=orm.document_id,
            warning_type=orm.warning_type,
            message=orm.message,
            component_name=orm.component_name,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            source_metadata=json_to_source_metadata(orm.source_metadata_json),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )
