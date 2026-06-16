import json

from src.domain.document.entities import DocumentSection
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import SectionORM


class SectionMapper:
    @staticmethod
    def to_orm(section: DocumentSection) -> SectionORM:
        return SectionORM(
            id=section.section_id,
            document_id=section.document_id,
            title=section.title,
            level=section.level,
            parent_section_id=section.parent_section_id,
            section_path=json.dumps(section.section_path),
            page_start=section.source.page_start,
            page_end=section.source.page_end,
            sequence_number=section.sequence_number,
            reading_order_start=section.reading_order_start,
            reading_order_end=section.reading_order_end,
            created_at=section.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: SectionORM, element_ids: list[str] | None = None) -> DocumentSection:
        return DocumentSection(
            section_id=orm.id,
            document_id=orm.document_id,
            title=orm.title,
            level=orm.level,
            parent_section_id=orm.parent_section_id,
            section_path=json.loads(orm.section_path or "[]"),
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            element_ids=element_ids or [],
            sequence_number=orm.sequence_number,
            reading_order_start=orm.reading_order_start,
            reading_order_end=orm.reading_order_end,
        )