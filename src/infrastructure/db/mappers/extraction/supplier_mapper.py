from src.domain.extraction import Supplier
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import SupplierORM


class SupplierMapper:
    @staticmethod
    def to_orm(
        supplier: Supplier,
        extraction_id: str | None = None,
    ) -> SupplierORM:
        return SupplierORM(
            id=supplier.supplier_id,
            extraction_id=extraction_id,
            document_id=supplier.document_id,
            name=supplier.name,
            website=supplier.website,
            country=supplier.country,
            source_chunk_id=supplier.source_chunk_id,
            page_start=supplier.source.page_start,
            page_end=supplier.source.page_end,
            confidence_score=supplier.confidence_score,
            requires_human_review=supplier.requires_human_review,
            created_at=supplier.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: SupplierORM) -> Supplier:
        return Supplier(
            supplier_id=orm.id,
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
