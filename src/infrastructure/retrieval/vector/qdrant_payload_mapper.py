from qdrant_client.http.models import models

from src.domain.common import ChunkType, SourceLocation
from src.domain.document.entities import DocumentChunk
from src.domain.retrieval import RetrievedChunk


class QdrantPayloadMapper:
    @staticmethod
    def from_chunk(
        chunk: DocumentChunk,
        *,
        document_type: str | None = None,
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
        }
        if document_type is not None:
            payload["document_type"] = document_type
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

        metadata = {
            "sequence_number": str(payload.get("sequence_number") or ""),
            "chunk_index": str(payload.get("chunk_index") or ""),
            "chunk_total": str(payload.get("chunk_total") or ""),
        }
        if payload.get("document_type") is not None:
            metadata["document_type"] = str(payload.get("document_type"))

        return RetrievedChunk(
            chunk_id=str(payload.get("chunk_id") or point.id),
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
            source=SourceLocation(
                page_start=QdrantPayloadMapper._coerce_int(payload.get("page_start")),
                page_end=QdrantPayloadMapper._coerce_int(payload.get("page_end")),
            ),
            metadata=metadata,
        )

    @staticmethod
    def _coerce_int(value: object) -> int | None:
        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None
