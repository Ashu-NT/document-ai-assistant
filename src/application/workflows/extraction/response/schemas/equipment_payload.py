from __future__ import annotations

from pydantic import AliasChoices, Field

from src.application.workflows.extraction.response.schemas.extraction_payload_base import (
    _ExtractionItemBase,
)


class EquipmentPayload(_ExtractionItemBase):
    name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("name", "equipment_name"),
    )
    model_number: str | None = Field(
        default=None,
        validation_alias=AliasChoices("model_number", "model"),
    )
    serial_number: str | None = Field(
        default=None,
        validation_alias=AliasChoices("serial_number", "serial"),
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
