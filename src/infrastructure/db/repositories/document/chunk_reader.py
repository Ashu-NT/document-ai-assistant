from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.document.entities import DocumentChunk
from src.infrastructure.db.mappers.document.chunk_mapper import ChunkMapper
from src.infrastructure.db.orm_models import ChunkORM


class ChunkReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_chunks_by_document(self, document_id: str) -> list[DocumentChunk]:
        statement = (
            select(ChunkORM)
            .where(ChunkORM.document_id == document_id)
            .order_by(ChunkORM.sequence_number)
        )

        rows = self.session.execute(statement).scalars().all()

        return [ChunkMapper.to_domain(row) for row in rows]

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[DocumentChunk]:
        if not chunk_ids:
            return []

        statement = select(ChunkORM).where(ChunkORM.id.in_(chunk_ids))

        rows = self.session.execute(statement).scalars().all()

        return [ChunkMapper.to_domain(row) for row in rows]