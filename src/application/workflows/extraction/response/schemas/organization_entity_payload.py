from __future__ import annotations

from pydantic import AliasChoices, Field

from src.application.workflows.extraction.response.schemas.extraction_payload_base import (
    _ExtractionItemBase,
)


class ManufacturerPayload(_ExtractionItemBase):
    name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("name", "manufacturer_name"),
    )
    website: str | None = Field(
        default=None,
        validation_alias=AliasChoices("website", "url"),
    )
    country: str | None = None
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


class SupplierPayload(_ExtractionItemBase):
    name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("name", "supplier_name"),
    )
    website: str | None = Field(
        default=None,
        validation_alias=AliasChoices("website", "url"),
    )
    country: str | None = None
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
