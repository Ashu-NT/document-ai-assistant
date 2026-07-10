from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.domain.document import DocumentChunk
from src.domain.extraction import ExtractedIdentifier


class ExtractedIdentifierBuilder:
    def __init__(self, support: ExtractionBuilderSupport) -> None:
        self._support = support

    def build(
        self,
        payload: dict[str, Any],
        *,
        chunk_lookup: dict[str, DocumentChunk],
        default_source_chunk_id: str | None,
        default_confidence: float,
    ) -> ExtractedIdentifier:
        support = self._support
        raw_value = support.required_text(
            payload,
            field_name="identifiers.raw_value",
            keys=("raw_value", "value"),
        )
        identifier_type = (
            support.optional_text(payload, "identifier_type", "type") or "unknown"
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
            item_type="identifiers",
        )

        return ExtractedIdentifier(
            raw_value=raw_value,
            identifier_type=identifier_type,
            source_chunk_id=source_chunk_id,
            confidence_score=confidence_score,
            requires_human_review=(
                support.resolve_requires_human_review(
                    support.pick(payload, "requires_human_review", "requires_review"),
                    confidence_score,
                )
                or chunk_id_invalid
            ),
        )
