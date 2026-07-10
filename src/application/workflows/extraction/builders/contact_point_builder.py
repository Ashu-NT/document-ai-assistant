from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.application.workflows.extraction.extraction_enum_coercion import (
    resolve_contact_owner_type,
    resolve_contact_point_type,
)
from src.domain.document import DocumentChunk
from src.domain.extraction import ContactPoint
from src.shared.ids import IdGenerator


class ContactPointBuilder:
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
    ) -> ContactPoint:
        support = self._support
        value = support.required_text(
            payload,
            field_name="contact_points.value",
            keys=("value",),
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
            item_type="contact_points",
        )
        contact_type = resolve_contact_point_type(
            support.pick(payload, "contact_type", "type")
        )
        owner_entity_type = resolve_contact_owner_type(
            support.pick(payload, "owner_entity_type")
        )

        return ContactPoint(
            contact_point_id=self._id_generator.new_id("contact_point"),
            document_id=document_id,
            contact_type=contact_type,
            value=value,
            label=support.optional_text(payload, "label"),
            owner_name=support.optional_text(payload, "owner_name"),
            owner_entity_type=owner_entity_type,
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
