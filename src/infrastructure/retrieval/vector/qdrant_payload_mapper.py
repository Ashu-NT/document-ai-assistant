import json

from qdrant_client.http.models import models

from src.domain.common import ChunkType, SourceLocation
from src.domain.document.entities import DocumentChunk
from src.domain.document.value_objects import ChunkStatistics
from src.domain.retrieval.citation import Citation
from src.domain.retrieval import RetrievedChunk


class QdrantPayloadMapper:
    @staticmethod
    def from_chunk(
        chunk: DocumentChunk,
        *,
        document_type: str | None = None,
        identifier_values: list[str] | None = None,
    ) -> dict:
        payload = {
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "section_id": chunk.section_id,
            "section_path": list(chunk.section_path),
            "chunk_type": chunk.chunk_type.value,
            "content": chunk.content,
            "sequence_number": chunk.sequence_number,
            "chunk_index": chunk.chunk_index,
            "chunk_total": chunk.chunk_total,
            "page_start": chunk.source.page_start,
            "page_end": chunk.source.page_end,
            "table_ids": list(chunk.table_ids),
        }
        if chunk.logical_table_family_id is not None:
            payload["logical_table_family_id"] = chunk.logical_table_family_id
        if chunk.logical_table_family_index is not None:
            payload["logical_table_family_index"] = chunk.logical_table_family_index
        if chunk.logical_table_family_total is not None:
            payload["logical_table_family_total"] = chunk.logical_table_family_total
        if chunk.logical_table_continuation_role is not None:
            payload["logical_table_continuation_role"] = (
                chunk.logical_table_continuation_role
            )
        if chunk.table_category is not None:
            payload["table_category"] = chunk.table_category
        if chunk.table_category_confidence is not None:
            payload["table_category_confidence"] = chunk.table_category_confidence
        if chunk.table_row_start is not None:
            payload["table_row_start"] = chunk.table_row_start
        if chunk.table_row_end is not None:
            payload["table_row_end"] = chunk.table_row_end
        if chunk.statistics is not None:
            payload["char_count"] = chunk.statistics.char_count
            if chunk.statistics.token_count_estimate is not None:
                payload["token_count_estimate"] = (
                    chunk.statistics.token_count_estimate
                )
        if document_type is not None:
            payload["document_type"] = document_type
        if identifier_values:
            payload["identifier_values"] = identifier_values
        return payload

    @staticmethod
    def to_retrieved_chunk(
        point: models.ScoredPoint,
        *,
        retrieval_source: str = "dense",
    ) -> RetrievedChunk:
        payload = point.payload or {}
        raw_section_path = payload.get("section_path") or []
        section_path = (
            [str(part) for part in raw_section_path]
            if isinstance(raw_section_path, list)
            else []
        )
        source = SourceLocation(
            page_start=QdrantPayloadMapper._coerce_int(payload.get("page_start")),
            page_end=QdrantPayloadMapper._coerce_int(payload.get("page_end")),
        )
        chunk_id = str(payload.get("chunk_id") or point.id)

        metadata = {
            "sequence_number": str(payload.get("sequence_number") or ""),
            "chunk_index": str(payload.get("chunk_index") or ""),
            "chunk_total": str(payload.get("chunk_total") or ""),
        }
        if payload.get("document_type") is not None:
            metadata["document_type"] = str(payload.get("document_type"))
        if payload.get("table_ids") is not None:
            metadata["table_ids"] = json.dumps(payload.get("table_ids"))
        for key in (
            "logical_table_family_id",
            "logical_table_family_index",
            "logical_table_family_total",
            "logical_table_continuation_role",
            "table_category",
            "table_category_confidence",
            "table_row_start",
            "table_row_end",
        ):
            if payload.get(key) is not None:
                metadata[key] = str(payload.get(key))

        raw_identifier_values = payload.get("identifier_values") or []
        identifier_values = (
            [str(value) for value in raw_identifier_values]
            if isinstance(raw_identifier_values, list)
            else []
        )

        return RetrievedChunk(
            chunk_id=chunk_id,
            document_id=str(payload.get("document_id") or ""),
            content=str(payload.get("content") or ""),
            score=float(point.score),
            retrieval_source=retrieval_source,
            chunk_type=ChunkType(str(payload.get("chunk_type") or ChunkType.UNKNOWN.value)),
            section_id=(
                str(payload.get("section_id"))
                if payload.get("section_id") is not None
                else None
            ),
            section_path=section_path,
            source=source,
            citation=Citation(
                citation_id=f"cit_{chunk_id}",
                document_id=str(payload.get("document_id") or ""),
                chunk_id=chunk_id,
                section_id=(
                    str(payload.get("section_id"))
                    if payload.get("section_id") is not None
                    else None
                ),
                document_name=(
                    str(
                        payload.get("document_name")
                        or payload.get("document_title")
                        or ""
                    ).strip()
                    or None
                ),
                section_title=section_path[-1] if section_path else None,
                source=source,
            ),
            statistics=QdrantPayloadMapper._statistics_from_payload(payload),
            metadata=metadata,
            identifier_values=identifier_values,
        )

    @staticmethod
    def _coerce_int(value: object) -> int | None:
        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _statistics_from_payload(payload: dict) -> ChunkStatistics | None:
        char_count = QdrantPayloadMapper._coerce_int(payload.get("char_count"))
        token_count_estimate = QdrantPayloadMapper._coerce_int(
            payload.get("token_count_estimate")
        )
        if char_count is None and token_count_estimate is None:
            return None
        return ChunkStatistics(
            char_count=char_count or len(str(payload.get("content") or "")),
            token_count_estimate=token_count_estimate,
        )
