from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.document.entities import DocumentChunk
from src.infrastructure.db.mappers import ChunkMapper
from src.infrastructure.db.orm_models import ChunkORM
from src.shared.exceptions import DatabaseError

class ChunkReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_chunks_by_document(self, document_id: str) -> list[DocumentChunk]:
        try:
            statement = (
                select(ChunkORM)
                .where(ChunkORM.document_id == document_id)
                .order_by(ChunkORM.sequence_number)
            )

            rows = self.session.execute(statement).scalars().all()

            return [ChunkMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list chunks by document.",
                details={"document_id": document_id},
            ) from exc

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[DocumentChunk]:
        if not chunk_ids:
            return []

        try:
            statement = select(ChunkORM).where(ChunkORM.id.in_(chunk_ids))
            rows = self.session.execute(statement).scalars().all()

            return [ChunkMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to get chunks by ids.",
                details={"chunk_ids": chunk_ids},
            ) from exc