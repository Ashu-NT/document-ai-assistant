import json

from src.domain.common import ChunkType
from src.domain.document.value_objects import ChunkStatistics
from src.domain.retrieval import RetrievedChunk
from src.infrastructure.db.mappers.common import columns_to_source_location
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
        if row.table_ids_json:
            metadata["table_ids"] = row.table_ids_json
        if row.logical_table_family_id:
            metadata["logical_table_family_id"] = row.logical_table_family_id
        if row.logical_table_family_index is not None:
            metadata["logical_table_family_index"] = str(row.logical_table_family_index)
        if row.logical_table_family_total is not None:
            metadata["logical_table_family_total"] = str(row.logical_table_family_total)
        if row.logical_table_continuation_role:
            metadata["logical_table_continuation_role"] = (
                row.logical_table_continuation_role
            )
        if row.table_category:
            metadata["table_category"] = row.table_category
        if row.table_category_confidence is not None:
            metadata["table_category_confidence"] = str(
                row.table_category_confidence
            )
        if row.table_row_start is not None:
            metadata["table_row_start"] = str(row.table_row_start)
        if row.table_row_end is not None:
            metadata["table_row_end"] = str(row.table_row_end)
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
            source=columns_to_source_location(
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
