import json

from src.domain.common import ChunkType, SourceLocation
from src.domain.document.value_objects import ChunkStatistics
from src.domain.retrieval import RetrievedChunk
from src.infrastructure.db.orm_models import ChunkORM


class RetrievedChunkMapper:
    @staticmethod
    def from_chunk_orm(
        row: ChunkORM,
        *,
        score: float = 1.0,
        retrieval_source: str = "sql_keyword",
        extra_metadata: dict[str, str] | None = None,
        identifier_values: list[str] | None = None,
    ) -> RetrievedChunk:
        metadata = {
            "sequence_number": str(row.sequence_number),
            "chunk_index": str(row.chunk_index),
            "chunk_total": str(row.chunk_total),
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        return RetrievedChunk(
            chunk_id=row.id,
            document_id=row.document_id,
            content=row.content,
            score=score,
            retrieval_source=retrieval_source,
            chunk_type=ChunkType(row.chunk_type),
            section_id=row.section_id,
            section_path=json.loads(row.section_path or "[]"),
            source=SourceLocation(
                page_start=row.page_start,
                page_end=row.page_end,
            ),
            statistics=ChunkStatistics(
                char_count=row.char_count or len(row.content or ""),
                token_count_estimate=row.token_count_estimate,
            )
            if row.char_count is not None or row.token_count_estimate is not None
            else None,
            metadata=metadata,
            identifier_values=list(identifier_values) if identifier_values else [],
        )
