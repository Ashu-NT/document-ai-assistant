from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.builders.extraction_builder_support import (
    ExtractionBuilderSupport,
)
from src.domain.document import DocumentChunk
from src.domain.extraction import Manufacturer, Supplier
from src.shared.ids import IdGenerator

# Manufacturer and Supplier builders share the same shape (name + website +
# country) and previously had near-identical `_build_manufacturer`/
# `_build_supplier` methods on ExtractionWorkflow. Co-located here as two
# small "organization entity" builders rather than merged into one class --
# they map to two distinct domain types with their own id prefixes/field
# names, so a forced shared base class would be more abstraction than the
# actual duplication (a handful of lines) warrants.


class ManufacturerBuilder:
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
    ) -> Manufacturer:
        support = self._support
        name = support.required_text(
            payload,
            field_name="manufacturers.name",
            keys=("name", "manufacturer_name"),
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
            item_type="manufacturers",
        )

        return Manufacturer(
            manufacturer_id=self._id_generator.new_id("manufacturer"),
            document_id=document_id,
            name=name,
            website=support.optional_text(payload, "website", "url"),
            country=support.optional_text(payload, "country"),
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


class SupplierBuilder:
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
    ) -> Supplier:
        support = self._support
        name = support.required_text(
            payload,
            field_name="suppliers.name",
            keys=("name", "supplier_name"),
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
            item_type="suppliers",
        )

        return Supplier(
            supplier_id=self._id_generator.new_id("supplier"),
            document_id=document_id,
            name=name,
            website=support.optional_text(payload, "website", "url"),
            country=support.optional_text(payload, "country"),
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
