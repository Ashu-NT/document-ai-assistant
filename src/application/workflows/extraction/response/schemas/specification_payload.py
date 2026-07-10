from __future__ import annotations

from pydantic import AliasChoices, Field

from src.application.workflows.extraction.response.schemas.extraction_payload_base import (
    _ExtractionItemBase,
)


class SpecificationPayload(_ExtractionItemBase):
    parameter: str | None = None
    value: str | None = None
    unit: str | None = None
    component_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("component_name", "component"),
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
