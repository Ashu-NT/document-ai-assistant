from __future__ import annotations

import json
from typing import Sequence

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class StructuredSourceBuilder:
    """Maps RetrievedChunk -> AnswerSource. Extracted out of
    AnswerContextOrganizer (plan Phase 5) so the organizer stays
    orchestration-only -- this is the one piece of real extraction/mapping
    logic that was embedded directly in it."""

    def build_sources(self, chunks: Sequence[RetrievedChunk]) -> list[AnswerSource]:
        return [
            self._to_source(index + 1, chunk) for index, chunk in enumerate(chunks)
        ]

    @staticmethod
    def _to_source(source_number: int, chunk: RetrievedChunk) -> AnswerSource:
        citation = chunk.citation
        section_path = " > ".join(chunk.section_path) if chunk.section_path else None
        chunk_name = (
            (citation.section_title if citation is not None else None)
            or (chunk.section_path[-1] if chunk.section_path else None)
            or chunk.chunk_type.value
        )
        document_title = None
        if citation is not None and citation.document_name:
            document_title = citation.document_name
        elif chunk.metadata.get("document_title"):
            document_title = chunk.metadata["document_title"]
        return AnswerSource(
            source_number=source_number,
            chunk_id=chunk.chunk_id,
            chunk_name=chunk_name,
            chunk_type=chunk.chunk_type.value,
            document_id=chunk.document_id,
            document_title=document_title,
            section_path=section_path,
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
            score=chunk.score,
            content=chunk.content,
            table_rows=StructuredSourceBuilder._decode_table_rows(chunk.metadata),
            table_shape=chunk.metadata.get("table_shape") or None,
            table_structure_quality=StructuredSourceBuilder._coerce_float(
                chunk.metadata.get("table_structure_quality")
            ),
            table_header_paths=StructuredSourceBuilder._decode_table_header_paths(
                chunk.metadata
            ),
            table_axis_summary=StructuredSourceBuilder._decode_table_axis_summary(
                chunk.metadata
            ),
            retrieval_source=chunk.retrieval_source,
            section_id=chunk.section_id,
            statistics=chunk.statistics,
            identifier_values=list(chunk.identifier_values),
            metadata=dict(chunk.metadata),
            collapsed_chunk_ids=StructuredSourceBuilder._decode_collapsed_chunk_ids(
                chunk.metadata
            ),
        )

    @staticmethod
    def _decode_collapsed_chunk_ids(metadata: dict[str, str]) -> list[str]:
        raw = metadata.get("dedup_collapsed_chunk_ids", "")
        return [
            chunk_id.strip()
            for chunk_id in raw.split(",")
            if chunk_id.strip()
        ]

    @staticmethod
    def _decode_table_rows(metadata: dict[str, str]) -> list[list[str]] | None:
        raw = metadata.get("table_rows_json")
        if not raw:
            return None
        try:
            decoded = json.loads(raw)
        except ValueError:
            return None
        return decoded if isinstance(decoded, list) else None

    @staticmethod
    def _decode_table_header_paths(metadata: dict[str, str]) -> list[list[str]]:
        raw = metadata.get("table_header_paths_json")
        if not raw:
            return []
        try:
            decoded = json.loads(raw)
        except ValueError:
            return []
        if not isinstance(decoded, list):
            return []
        cleaned: list[list[str]] = []
        for path in decoded:
            if not isinstance(path, list):
                continue
            values = [str(part).strip() for part in path if str(part).strip()]
            if values:
                cleaned.append(values)
        return cleaned

    @staticmethod
    def _decode_table_axis_summary(metadata: dict[str, str]) -> dict[str, str]:
        raw = metadata.get("table_axis_summary")
        if not raw:
            return {}
        try:
            decoded = json.loads(raw)
        except ValueError:
            return {}
        if not isinstance(decoded, dict):
            return {}
        return {
            str(key).strip(): str(value).strip()
            for key, value in decoded.items()
            if str(key).strip() and str(value).strip()
        }

    @staticmethod
    def _coerce_float(value: str | None) -> float | None:
        if not value:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
