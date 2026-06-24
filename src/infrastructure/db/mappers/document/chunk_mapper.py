import json

from src.domain.common import ChunkType
from src.domain.document.entities import DocumentChunk
from src.domain.document.value_objects import ChunkStatistics
from src.infrastructure.db.mappers.common.source_location_mapper import (
    columns_to_source_location,
)
from src.infrastructure.db.orm_models import ChunkORM


class ChunkMapper:
    @staticmethod
    def to_orm(chunk: DocumentChunk) -> ChunkORM:
        return ChunkORM(
            id=chunk.chunk_id,
            document_id=chunk.document_id,
            section_id=chunk.section_id,
            content=chunk.content,
            embedding_text=chunk.embedding_text,
            chunk_type=chunk.chunk_type.value,
            chunk_type_source=chunk.chunk_type_source,
            section_path=json.dumps(chunk.section_path),
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
            sequence_number=chunk.sequence_number,
            chunk_index=chunk.chunk_index,
            chunk_total=chunk.chunk_total,
            char_count=chunk.statistics.char_count if chunk.statistics else None,
            token_count_estimate=(
                chunk.statistics.token_count_estimate if chunk.statistics else None
            ),
            created_at=chunk.audit.created_at,
        )

    @staticmethod
    def to_domain(
        orm: ChunkORM,
        element_ids: list[str] | None = None,
        table_ids: list[str] | None = None,
        picture_ids: list[str] | None = None,
    ) -> DocumentChunk:
        return DocumentChunk(
            chunk_id=orm.id,
            document_id=orm.document_id,
            section_id=orm.section_id,
            content=orm.content,
            embedding_text=orm.embedding_text,
            chunk_type=ChunkType(orm.chunk_type),
            chunk_type_source=orm.chunk_type_source or "deterministic",
            section_path=json.loads(orm.section_path or "[]"),
            element_ids=element_ids or [],
            table_ids=table_ids or [],
            picture_ids=picture_ids or [],
            source=columns_to_source_location(
                page_start=orm.page_start,
                page_end=orm.page_end,
            ),
            sequence_number=orm.sequence_number,
            chunk_index=orm.chunk_index,
            chunk_total=orm.chunk_total,
            statistics=ChunkStatistics(
                char_count=orm.char_count or len(orm.content),
                token_count_estimate=orm.token_count_estimate,
            ),
        )