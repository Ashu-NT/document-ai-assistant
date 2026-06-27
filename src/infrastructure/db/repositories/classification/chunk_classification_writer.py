from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.classification import ChunkClassification
from src.infrastructure.db.mappers import (
    ChunkClassificationMapper,
)
from src.infrastructure.db.orm_models import ChunkClassificationORM
from src.shared.exceptions import DatabaseError


class ChunkClassificationWriter:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, classification: ChunkClassification) -> None:
        try:
            self.session.execute(
                delete(ChunkClassificationORM).where(
                    ChunkClassificationORM.chunk_id == classification.chunk_id
                )
            )
            self.session.merge(
                ChunkClassificationMapper.to_orm(classification)
            )
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save chunk classification.",
                details={
                    "document_id": classification.document_id,
                    "chunk_id": classification.chunk_id,
                },
            ) from exc
