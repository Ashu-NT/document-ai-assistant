from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval import RetrievedChunk
from src.infrastructure.db.orm_models import ChunkORM
from src.shared.exceptions import DatabaseError


class SqlKeywordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search_chunks(
        self,
        query: str,
        limit: int,
    ) -> list[RetrievedChunk]:
        try:
            pattern = f"%{query}%"

            statement = (
                select(ChunkORM)
                .where(
                    or_(
                        ChunkORM.content.ilike(pattern),
                        ChunkORM.embedding_text.ilike(pattern),
                    )
                )
                .limit(limit)
            )

            rows = self.session.execute(statement).scalars().all()

            return [
                RetrievedChunk(
                    chunk_id=row.id,
                    document_id=row.document_id,
                    content=row.content,
                    score=1.0,
                    retrieval_source="sql_keyword",
                    chunk_type=ChunkType(row.chunk_type),
                    section_id=row.section_id,
                    section_path=[],
                    source=SourceLocation(
                        page_start=row.page_start,
                        page_end=row.page_end,
                    ),
                )
                for row in rows
            ]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search chunks by SQL keyword.",
                details={"query": query, "limit": limit},
            ) from exc