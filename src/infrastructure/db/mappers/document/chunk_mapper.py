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
            element_ids_json=ChunkMapper._dump_string_list(chunk.element_ids),
            table_ids_json=ChunkMapper._dump_string_list(chunk.table_ids),
            picture_ids_json=ChunkMapper._dump_string_list(chunk.picture_ids),
            logical_table_family_id=chunk.logical_table_family_id,
            logical_table_family_index=chunk.logical_table_family_index,
            logical_table_family_total=chunk.logical_table_family_total,
            logical_table_continuation_role=chunk.logical_table_continuation_role,
            table_category=chunk.table_category,
            table_category_confidence=chunk.table_category_confidence,
            table_row_start=chunk.table_row_start,
            table_row_end=chunk.table_row_end,
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
            section_path=ChunkMapper._load_string_list(orm.section_path),
            element_ids=(
                list(element_ids)
                if element_ids is not None
                else ChunkMapper._load_string_list(orm.element_ids_json)
            ),
            table_ids=(
                list(table_ids)
                if table_ids is not None
                else ChunkMapper._load_string_list(orm.table_ids_json)
            ),
            picture_ids=(
                list(picture_ids)
                if picture_ids is not None
                else ChunkMapper._load_string_list(orm.picture_ids_json)
            ),
            logical_table_family_id=orm.logical_table_family_id,
            logical_table_family_index=orm.logical_table_family_index,
            logical_table_family_total=orm.logical_table_family_total,
            logical_table_continuation_role=orm.logical_table_continuation_role,
            table_category=orm.table_category,
            table_category_confidence=orm.table_category_confidence,
            table_row_start=orm.table_row_start,
            table_row_end=orm.table_row_end,
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

    @staticmethod
    def _dump_string_list(values: list[str]) -> str:
        return json.dumps(list(values))

    @staticmethod
    def _load_string_list(raw_value: str | None) -> list[str]:
        if not raw_value:
            return []

        try:
            loaded = json.loads(raw_value)
        except json.JSONDecodeError:
            return []

        if not isinstance(loaded, list):
            return []

        return [str(value) for value in loaded if str(value)]
