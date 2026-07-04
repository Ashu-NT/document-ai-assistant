from src.domain.extraction import Specification
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import SpecificationORM


class SpecificationMapper:
    @staticmethod
    def to_orm(
        specification: Specification,
        extraction_id: str | None = None,
    ) -> SpecificationORM:
        return SpecificationORM(
            id=specification.specification_id,
            extraction_id=extraction_id,
            document_id=specification.document_id,
            parameter=specification.parameter,
            value=specification.value,
            unit=specification.unit,
            component_name=specification.component_name,
            source_chunk_id=specification.source_chunk_id,
            page_start=specification.source.page_start,
            page_end=specification.source.page_end,
            confidence_score=specification.confidence_score,
            requires_human_review=specification.requires_human_review,
            created_at=specification.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: SpecificationORM) -> Specification:
        return Specification(
            specification_id=orm.id,
            document_id=orm.document_id,
            parameter=orm.parameter,
            value=orm.value,
            unit=orm.unit,
            component_name=orm.component_name,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )
