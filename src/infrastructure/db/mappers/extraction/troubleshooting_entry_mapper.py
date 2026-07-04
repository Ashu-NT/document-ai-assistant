from src.domain.extraction import TroubleshootingEntry
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import TroubleshootingEntryORM


class TroubleshootingEntryMapper:
    @staticmethod
    def to_orm(
        troubleshooting_entry: TroubleshootingEntry,
        extraction_id: str | None = None,
    ) -> TroubleshootingEntryORM:
        return TroubleshootingEntryORM(
            id=troubleshooting_entry.troubleshooting_id,
            extraction_id=extraction_id,
            document_id=troubleshooting_entry.document_id,
            symptom=troubleshooting_entry.symptom,
            cause=troubleshooting_entry.cause,
            remedy=troubleshooting_entry.remedy,
            component_name=troubleshooting_entry.component_name,
            equipment_id=troubleshooting_entry.equipment_id,
            source_chunk_id=troubleshooting_entry.source_chunk_id,
            page_start=troubleshooting_entry.source.page_start,
            page_end=troubleshooting_entry.source.page_end,
            confidence_score=troubleshooting_entry.confidence_score,
            requires_human_review=troubleshooting_entry.requires_human_review,
            created_at=troubleshooting_entry.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: TroubleshootingEntryORM) -> TroubleshootingEntry:
        return TroubleshootingEntry(
            troubleshooting_id=orm.id,
            document_id=orm.document_id,
            symptom=orm.symptom,
            cause=orm.cause,
            remedy=orm.remedy,
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
