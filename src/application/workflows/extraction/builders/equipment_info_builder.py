from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.domain.document import DocumentChunk
from src.domain.extraction import EquipmentInfo
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator


def _normalize_for_grounding(text: str) -> str:
    return " ".join(text.split()).casefold()


def _designators_supported_by_chunk(
    *,
    model_number: str | None,
    serial_number: str | None,
    chunk_content: str,
) -> bool:
    normalized_content = _normalize_for_grounding(chunk_content)
    for designator in (model_number, serial_number):
        if designator and _normalize_for_grounding(designator) not in normalized_content:
            return False
    return True


class EquipmentInfoBuilder:
    def __init__(
        self,
        id_generator: IdGenerator,
        support: ExtractionBuilderSupport,
    ) -> None:
        self._id_generator = id_generator
        self._support = support

    def build(
        self,
        payload: dict[str, Any],
        *,
        document_id: str,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> EquipmentInfo:
        support = self._support
        name = support.optional_text(payload, "name", "equipment_name")
        model_number = support.optional_text(payload, "model_number", "model")
        serial_number = support.optional_text(payload, "serial_number", "serial")
        manufacturer_name = support.optional_text(
            payload,
            "manufacturer_name",
            "manufacturer",
        )

        if not any(
            [
                name,
                model_number,
                serial_number,
                manufacturer_name,
            ]
        ):
            raise SchemaValidationError(
                "equipment items must contain at least one supported field.",
                details={"equipment": payload},
            )

        confidence_score = support.parse_confidence(
            support.pick(payload, "confidence_score", "confidence")
        )
        if confidence_score is None:
            confidence_score = default_confidence

        source_chunk_id, chunk_id_invalid = support.resolve_source_chunk_id(
            payload,
            chunk_lookup=chunk_lookup,
            default_source_chunk_id=default_source_chunk_id,
            item_type="equipment",
        )

        evidence_unsupported = False
        if source_chunk_id is not None and not chunk_id_invalid:
            source_chunk = chunk_lookup.get(source_chunk_id)
            if source_chunk is not None and not _designators_supported_by_chunk(
                model_number=model_number,
                serial_number=serial_number,
                chunk_content=source_chunk.content,
            ):
                evidence_unsupported = True
                support.equipment_unsupported_evidence_events.append(
                    {
                        "source_chunk_id": source_chunk_id,
                        "model_number": model_number,
                        "serial_number": serial_number,
                    }
                )

        return EquipmentInfo(
            equipment_id=self._id_generator.new_id("equipment"),
            document_id=document_id,
            name=name,
            model_number=model_number,
            serial_number=serial_number,
            manufacturer_name=manufacturer_name,
            source_chunk_id=source_chunk_id,
            source=support.resolve_source_location(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            source_metadata=support.build_source_metadata(
                source_chunk_id=source_chunk_id,
                chunk_lookup=chunk_lookup,
            ),
            confidence_score=confidence_score,
            requires_human_review=(
                support.resolve_requires_human_review(
                    support.pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
                or evidence_unsupported
            ),
        )
