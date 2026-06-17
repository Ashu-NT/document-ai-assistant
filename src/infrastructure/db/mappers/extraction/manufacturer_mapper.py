from src.domain.extraction import Manufacturer
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import ManufacturerORM


class ManufacturerMapper:
    @staticmethod
    def to_orm(
        manufacturer: Manufacturer,
        extraction_id: str | None = None,
    ) -> ManufacturerORM:
        return ManufacturerORM(
            id=manufacturer.manufacturer_id,
            extraction_id=extraction_id,
            document_id=manufacturer.document_id,
            name=manufacturer.name,
            website=manufacturer.website,
            country=manufacturer.country,
            source_chunk_id=manufacturer.source_chunk_id,
            page_start=manufacturer.source.page_start,
            page_end=manufacturer.source.page_end,
            confidence_score=manufacturer.confidence_score,
            requires_human_review=manufacturer.requires_human_review,
            created_at=manufacturer.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: ManufacturerORM) -> Manufacturer:
        return Manufacturer(
            manufacturer_id=orm.id,
            document_id=orm.document_id,
            name=orm.name,
            website=orm.website,
            country=orm.country,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )