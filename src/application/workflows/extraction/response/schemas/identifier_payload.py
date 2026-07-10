from __future__ import annotations

from pydantic import AliasChoices, Field

from src.application.workflows.extraction.response.schemas.extraction_payload_base import (
    _ExtractionItemBase,
)


class IdentifierPayload(_ExtractionItemBase):
    raw_value: str | None = Field(
        default=None,
        validation_alias=AliasChoices("raw_value", "value"),
    )
    identifier_type: str | None = Field(
        default=None,
        validation_alias=AliasChoices("identifier_type", "type"),
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
