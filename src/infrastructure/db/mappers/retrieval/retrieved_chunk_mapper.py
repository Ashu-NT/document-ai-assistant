from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval import RetrievedChunk
from src.infrastructure.db.orm_models import ChunkORM


class RetrievedChunkMapper:
    @staticmethod
    def from_chunk_orm(
        row: ChunkORM,
        *,
        score: float = 1.0,
        retrieval_source: str = "sql_keyword",
    ) -> RetrievedChunk:
        return RetrievedChunk(
            chunk_id=row.id,
            document_id=row.document_id,
            content=row.content,
            score=score,
            retrieval_source=retrieval_source,
            chunk_type=ChunkType(row.chunk_type),
            section_id=row.section_id,
            section_path=[],
            source=SourceLocation(
                page_start=row.page_start,
                page_end=row.page_end,
            ),
        )