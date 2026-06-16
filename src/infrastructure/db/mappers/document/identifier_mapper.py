from src.domain.common import IdentifierType
from src.domain.document.entities import Identifier
from src.infrastructure.db.orm_models import IdentifierORM


class IdentifierMapper:
    @staticmethod
    def to_orm(identifier: Identifier) -> IdentifierORM:
        return IdentifierORM(
            id=identifier.identifier_id,
            document_id=identifier.document_id,
            chunk_id=identifier.chunk_id,
            element_id=identifier.element_id,
            raw_value=identifier.raw_value,
            normalized_value=identifier.normalized_value or identifier.raw_value,
            identifier_type=identifier.identifier_type.value,
            confidence_score=identifier.confidence_score,
            created_at=identifier.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: IdentifierORM) -> Identifier:
        return Identifier(
            identifier_id=orm.id,
            document_id=orm.document_id,
            chunk_id=orm.chunk_id,
            element_id=orm.element_id,
            raw_value=orm.raw_value,
            normalized_value=orm.normalized_value,
            identifier_type=IdentifierType(orm.identifier_type),
            confidence_score=orm.confidence_score,
        )