from __future__ import annotations

from src.domain.common.enums import IdentifierType
from src.domain.common.value_objects import normalize_identifier
from src.domain.document import DocumentGraph
from src.domain.document.entities.identifier import Identifier
from src.domain.extraction.extraction_result import ExtractionResult
from src.shared.ids import IdGenerator, IdPrefix


class IdentifierPromotionService:
    def promote(
        self,
        extraction_result: ExtractionResult,
        document_graph: DocumentGraph,
        id_generator: IdGenerator,
    ) -> list[Identifier]:
        identifiers: list[Identifier] = []
        seen: set[tuple[str, str]] = set()
        document_id = document_graph.document.document_id
        valid_chunk_ids = set(document_graph.chunks.keys())

        for part in extraction_result.spare_parts:
            if part.has_part_number():
                chunk = document_graph.chunks.get(part.source_chunk_id or "")
                identifier = self._make(
                    document_id=document_id,
                    raw_value=part.part_number,
                    identifier_type=IdentifierType.PART_NUMBER,
                    source_chunk_id=part.source_chunk_id,
                    valid_chunk_ids=valid_chunk_ids,
                    confidence_score=part.confidence_score,
                    id_generator=id_generator,
                    seen=seen,
                    chunk=chunk,
                )
                if identifier is not None:
                    identifiers.append(identifier)

        for equipment in extraction_result.equipment:
            chunk = document_graph.chunks.get(equipment.source_chunk_id or "")
            for raw_value, identifier_type in (
                (equipment.model_number, IdentifierType.MODEL_NUMBER),
                (equipment.serial_number, IdentifierType.SERIAL_NUMBER),
            ):
                if raw_value and raw_value.strip():
                    identifier = self._make(
                        document_id=document_id,
                        raw_value=raw_value,
                        identifier_type=identifier_type,
                        source_chunk_id=equipment.source_chunk_id,
                        valid_chunk_ids=valid_chunk_ids,
                        confidence_score=equipment.confidence_score,
                        id_generator=id_generator,
                        seen=seen,
                        chunk=chunk,
                    )
                    if identifier is not None:
                        identifiers.append(identifier)

        return identifiers

    @staticmethod
    def _make(
        *,
        document_id: str,
        raw_value: str | None,
        identifier_type: IdentifierType,
        source_chunk_id: str | None,
        valid_chunk_ids: set[str],
        confidence_score: float | None,
        id_generator: IdGenerator,
        seen: set[tuple[str, str]],
        chunk=None,
    ) -> Identifier | None:
        if not raw_value or not raw_value.strip():
            return None
        normalized = normalize_identifier(raw_value)
        if not normalized:
            return None
        dedup_key = (normalized, identifier_type.value)
        if dedup_key in seen:
            return None
        seen.add(dedup_key)
        chunk_id = (
            source_chunk_id
            if source_chunk_id and source_chunk_id in valid_chunk_ids
            else None
        )
        page_start = chunk.source.page_start if chunk and chunk_id else None
        page_end = chunk.source.page_end if chunk and chunk_id else None
        section_id = chunk.section_id if chunk and chunk_id else None
        return Identifier(
            identifier_id=id_generator.new_id(IdPrefix.IDENTIFIER),
            document_id=document_id,
            raw_value=raw_value.strip(),
            identifier_type=identifier_type,
            chunk_id=chunk_id,
            section_id=section_id,
            confidence_score=confidence_score,
            page_start=page_start,
            page_end=page_end,
        )
