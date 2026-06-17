from src.domain.extraction import SparePart
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import SparePartORM


class SparePartMapper:
    @staticmethod
    def to_orm(
        part: SparePart,
        extraction_id: str | None = None,
    ) -> SparePartORM:
        return SparePartORM(
            id=part.spare_part_id,
            extraction_id=extraction_id,
            document_id=part.document_id,
            part_number=part.part_number,
            description=part.description,
            quantity=part.quantity,
            component_name=part.component_name,
            manufacturer_name=part.manufacturer_name,
            source_chunk_id=part.source_chunk_id,
            page_start=part.source.page_start,
            page_end=part.source.page_end,
            confidence_score=part.confidence_score,
            requires_human_review=part.requires_human_review,
            created_at=part.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: SparePartORM) -> SparePart:
        return SparePart(
            spare_part_id=orm.id,
            document_id=orm.document_id,
            part_number=orm.part_number,
            description=orm.description,
            quantity=orm.quantity,
            component_name=orm.component_name,
            manufacturer_name=orm.manufacturer_name,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )