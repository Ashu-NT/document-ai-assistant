from src.domain.extraction import ContactPoint, ContactPointType
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
    json_to_source_metadata,
    source_metadata_to_json,
)
from src.infrastructure.db.orm_models import ContactPointORM


class ContactPointMapper:
    @staticmethod
    def to_orm(
        contact_point: ContactPoint,
        extraction_id: str | None = None,
    ) -> ContactPointORM:
        return ContactPointORM(
            id=contact_point.contact_point_id,
            extraction_id=extraction_id,
            document_id=contact_point.document_id,
            contact_type=contact_point.contact_type.value,
            value=contact_point.value,
            label=contact_point.label,
            owner_name=contact_point.owner_name,
            owner_entity_type=(
                contact_point.owner_entity_type.value
                if contact_point.owner_entity_type is not None
                else None
            ),
            source_chunk_id=contact_point.source_chunk_id,
            page_start=contact_point.source.page_start,
            page_end=contact_point.source.page_end,
            source_metadata_json=source_metadata_to_json(contact_point.source_metadata),
            confidence_score=contact_point.confidence_score,
            requires_human_review=contact_point.requires_human_review,
            created_at=contact_point.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: ContactPointORM) -> ContactPoint:
        from src.domain.extraction.semantic_relationship import SemanticEntityType

        owner_entity_type = None
        if orm.owner_entity_type:
            try:
                owner_entity_type = SemanticEntityType(orm.owner_entity_type)
            except ValueError:
                owner_entity_type = None

        return ContactPoint(
            contact_point_id=orm.id,
            document_id=orm.document_id,
            contact_type=ContactPointType(orm.contact_type),
            value=orm.value,
            label=orm.label,
            owner_name=orm.owner_name,
            owner_entity_type=owner_entity_type,
            source_chunk_id=orm.source_chunk_id,
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            source_metadata=json_to_source_metadata(orm.source_metadata_json),
            confidence_score=orm.confidence_score,
            requires_human_review=orm.requires_human_review,
        )
