import json

from src.domain.common import ElementType, ParserMetadata
from src.domain.elements import CanonicalElement
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import ElementORM


class ElementMapper:
    @staticmethod
    def to_orm(element: CanonicalElement) -> ElementORM:
        source = element.source
        bbox = source.bbox
        parser_extra = (
            element.parser_metadata.extra
            if element.parser_metadata is not None and element.parser_metadata.extra
            else None
        )

        return ElementORM(
            id=element.element_id,
            document_id=element.document_id,
            element_type=element.element_type.value,
            text=element.text,
            parent_section_id=element.parent_section_id,
            reading_order=element.reading_order,
            page_start=source.page_start,
            page_end=source.page_end,
            bbox_x1=bbox.x1 if bbox else None,
            bbox_y1=bbox.y1 if bbox else None,
            bbox_x2=bbox.x2 if bbox else None,
            bbox_y2=bbox.y2 if bbox else None,
            table_id=element.table_id,
            picture_id=element.picture_id,
            raw_source_type=(
                element.parser_metadata.raw_source_type
                if element.parser_metadata
                else None
            ),
            raw_ref=element.parser_metadata.raw_ref if element.parser_metadata else None,
            parser_extra_json=(
                json.dumps(parser_extra, sort_keys=True)
                if parser_extra is not None
                else None
            ),
            created_at=element.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: ElementORM) -> CanonicalElement:
        parser_metadata = None
        parser_extra = (
            json.loads(orm.parser_extra_json)
            if orm.parser_extra_json
            else {}
        )

        if orm.raw_source_type or orm.raw_ref or parser_extra:
            parser_metadata = ParserMetadata(
                parser_name="docling",
                raw_source_type=orm.raw_source_type,
                raw_ref=orm.raw_ref,
                extra=parser_extra,
            )

        return CanonicalElement(
            element_id=orm.id,
            document_id=orm.document_id,
            element_type=ElementType(orm.element_type),
            text=orm.text,
            parent_section_id=orm.parent_section_id,
            reading_order=orm.reading_order,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
                bbox_x1=orm.bbox_x1,
                bbox_y1=orm.bbox_y1,
                bbox_x2=orm.bbox_x2,
                bbox_y2=orm.bbox_y2,
            ),
            table_id=orm.table_id,
            picture_id=orm.picture_id,
            parser_metadata=parser_metadata,
        )
