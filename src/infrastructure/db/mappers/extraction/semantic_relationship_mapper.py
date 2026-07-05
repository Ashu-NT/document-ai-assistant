from src.domain.extraction import (
    SemanticEntityType,
    SemanticRelationship,
    SemanticRelationshipStatus,
    SemanticRelationshipType,
)
from src.infrastructure.db.orm_models import SemanticRelationshipORM


class SemanticRelationshipMapper:
    @staticmethod
    def to_orm(relationship: SemanticRelationship) -> SemanticRelationshipORM:
        return SemanticRelationshipORM(
            id=relationship.relationship_id,
            document_id=relationship.document_id,
            relationship_type=relationship.relationship_type.value,
            source_entity_type=relationship.source_entity_type.value,
            source_entity_id=relationship.source_entity_id,
            target_entity_type=relationship.target_entity_type.value,
            target_entity_id=relationship.target_entity_id,
            confidence_score=relationship.confidence_score,
            status=relationship.status.value,
            evidence=relationship.evidence,
            created_at=relationship.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: SemanticRelationshipORM) -> SemanticRelationship:
        return SemanticRelationship(
            relationship_id=orm.id,
            document_id=orm.document_id,
            relationship_type=SemanticRelationshipType(orm.relationship_type),
            source_entity_type=SemanticEntityType(orm.source_entity_type),
            source_entity_id=orm.source_entity_id,
            target_entity_type=SemanticEntityType(orm.target_entity_type),
            target_entity_id=orm.target_entity_id,
            confidence_score=orm.confidence_score,
            status=SemanticRelationshipStatus(orm.status),
            evidence=orm.evidence,
        )
