from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.domain.document import DocumentChunk
from src.domain.extraction import SparePart
from src.shared.exceptions import SchemaValidationError
from src.shared.ids import IdGenerator


class SparePartBuilder:
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
    ) -> SparePart:
        support = self._support
        part_number = support.optional_text(payload, "part_number", "part")
        description = support.optional_text(payload, "description")
        quantity = support.optional_text(payload, "quantity", "qty")
        component_name = support.optional_text(payload, "component_name", "component")
        manufacturer_name = support.optional_text(
            payload,
            "manufacturer_name",
            "manufacturer",
        )

        if not any(
            [
                part_number,
                description,
                quantity,
                component_name,
                manufacturer_name,
            ]
        ):
            raise SchemaValidationError(
                "spare_parts items must contain at least one supported field.",
                details={"spare_part": payload},
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
            item_type="spare_parts",
        )

        return SparePart(
            spare_part_id=self._id_generator.new_id("spare"),
            document_id=document_id,
            part_number=part_number,
            description=description,
            quantity=quantity,
            component_name=component_name,
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
            ),
        )
