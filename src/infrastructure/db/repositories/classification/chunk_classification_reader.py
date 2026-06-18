from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.classification import ChunkClassification
from src.infrastructure.db.mappers import ChunkClassificationMapper
from src.infrastructure.db.orm_models import ChunkClassificationORM
from src.shared.exceptions import DatabaseError


class ChunkClassificationReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, chunk_id: str) -> ChunkClassification | None:
        try:
            statement = select(ChunkClassificationORM).where(
                ChunkClassificationORM.chunk_id == chunk_id,
            )

            row = self.session.execute(statement).scalar_one_or_none()

            if row is None:
                return None

            return ChunkClassificationMapper.to_domain(row)

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load chunk classification.",
                details={"chunk_id": chunk_id},
            ) from exc

    def list_by_document(self, document_id: str) -> list[ChunkClassification]:
        try:
            statement = select(ChunkClassificationORM).where(
                ChunkClassificationORM.document_id == document_id,
            )

            rows = self.session.execute(statement).scalars().all()

            return [ChunkClassificationMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list chunk classifications by document.",
                details={"document_id": document_id},
            ) from exc