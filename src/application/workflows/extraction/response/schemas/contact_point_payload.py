from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, ConfigDict, Field, field_validator

from src.application.workflows.extraction.response.schemas.extraction_payload_base import (
    _ExtractionItemBase,
)
from src.domain.extraction.contact_point import ContactPointType
from src.domain.extraction.semantic_relationship import SemanticEntityType


class ContactPointPayload(_ExtractionItemBase):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    contact_type: ContactPointType = Field(
        default=ContactPointType.UNKNOWN,
        validation_alias=AliasChoices("contact_type", "type"),
    )
    value: str | None = None
    label: str | None = None
    owner_name: str | None = None
    owner_entity_type: SemanticEntityType | None = None
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

    @field_validator("contact_type", mode="before")
    @classmethod
    def _normalize_contact_type(cls, value: Any) -> Any:
        if value is None:
            return ContactPointType.UNKNOWN
        if isinstance(value, ContactPointType):
            return value
        normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
        if normalized in {"phone", "telephone", "telephone_number", "tel"}:
            return ContactPointType.PHONE_NUMBER
        if normalized in {"fax", "fax_number"}:
            return ContactPointType.FAX_NUMBER
        if normalized in {"email", "email_address", "e_mail"}:
            return ContactPointType.EMAIL_ADDRESS
        if normalized in {"website", "web", "web_address"}:
            return ContactPointType.URL
        try:
            return ContactPointType(normalized)
        except ValueError:
            return ContactPointType.UNKNOWN

    @field_validator("owner_entity_type", mode="before")
    @classmethod
    def _normalize_owner_entity_type(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, SemanticEntityType):
            if value in {
                SemanticEntityType.MANUFACTURER,
                SemanticEntityType.SUPPLIER,
            }:
                return value
            return None
        normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
        try:
            semantic_type = SemanticEntityType(normalized)
        except ValueError:
            return None
        if semantic_type in {
            SemanticEntityType.MANUFACTURER,
            SemanticEntityType.SUPPLIER,
        }:
            return semantic_type
        return None
