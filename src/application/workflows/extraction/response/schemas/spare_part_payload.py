from __future__ import annotations

from pydantic import AliasChoices, Field

from src.application.workflows.extraction.response.schemas.extraction_payload_base import (
    _ExtractionItemBase,
)


class SparePartPayload(_ExtractionItemBase):
    part_number: str | None = Field(
        default=None,
        validation_alias=AliasChoices("part_number", "part"),
    )
    description: str | None = None
    quantity: str | None = Field(
        default=None,
        validation_alias=AliasChoices("quantity", "qty"),
    )
    component_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("component_name", "component"),
    )
    manufacturer_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("manufacturer_name", "manufacturer"),
    )
    source_chunk_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("source_chunk_id", "chunk_id"),
    )
    confidence_score: float | None = Field(
        default=None,
        validation_alias=AliasChoices("confidence_score", "confidence"),
    )
    requires_human_review: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("requires_human_review", "requires_review"),
    )
