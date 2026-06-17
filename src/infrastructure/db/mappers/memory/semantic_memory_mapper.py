from domain.memory import SemanticMemoryReference
from infrastructure.db.orm_models import SemanticMemoryReferenceORM


class SemanticMemoryMapper:
    @staticmethod
    def to_orm(reference: SemanticMemoryReference) -> SemanticMemoryReferenceORM:
        return SemanticMemoryReferenceORM(
            id=reference.reference_id,
            source_id=reference.source_id,
            source_type=reference.source_type,
            vector_id=reference.vector_id,
            collection_name=reference.collection_name,
            created_at=reference.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: SemanticMemoryReferenceORM) -> SemanticMemoryReference:
        return SemanticMemoryReference(
            reference_id=orm.id,
            source_id=orm.source_id,
            source_type=orm.source_type,
            vector_id=orm.vector_id,
            collection_name=orm.collection_name,
        )