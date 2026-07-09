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
        self.save_many([classification])

    def save_many(self, classifications: list[ChunkClassification]) -> None:
        """Deletes any prior classification for each chunk_id, then inserts
        all the new rows in one batch.

        Uses session.add_all() rather than a per-item session.merge(): each
        classification's PK (classification_id) is always freshly minted
        (see ChunkClassificationMapper.to_orm), so merge()'s existence-check
        SELECT would always miss anyway -- the preceding chunk_id-scoped
        DELETE is what actually clears any stale row for that chunk.
        """
        if not classifications:
            return

        try:
            chunk_ids = [classification.chunk_id for classification in classifications]
            self.session.execute(
                delete(ChunkClassificationORM).where(
                    ChunkClassificationORM.chunk_id.in_(chunk_ids)
                )
            )
            self.session.add_all(
                ChunkClassificationMapper.to_orm(classification)
                for classification in classifications
            )
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save chunk classifications.",
                details={"chunk_ids": [c.chunk_id for c in classifications]},
            ) from exc
