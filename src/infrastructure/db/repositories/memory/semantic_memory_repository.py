from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.memory import SemanticMemoryReference
from src.infrastructure.db.mappers import SemanticMemoryMapper
from src.shared.exceptions import DatabaseError


class SemanticMemoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, reference: SemanticMemoryReference) -> None:
        try:
            self.session.merge(SemanticMemoryMapper.to_orm(reference))
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save semantic memory reference.",
                details={"reference_id": reference.reference_id},
            ) from exc