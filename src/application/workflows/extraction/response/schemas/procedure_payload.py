from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, ConfigDict, Field, field_validator

from src.application.workflows.extraction.response.schemas.extraction_payload_base import (
    _ExtractionItemBase,
    coerce_raw_list,
)
from src.domain.extraction import ProcedureType


class ProcedurePayload(_ExtractionItemBase):
    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    title: str | None = None
    procedure_type: ProcedureType = Field(
        default=ProcedureType.UNKNOWN,
        validation_alias=AliasChoices("procedure_type", "type"),
    )
    steps: list[str] = Field(default_factory=list)
    component_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("component_name", "component"),
    )
    equipment_reference: str | None = Field(
        default=None,
        validation_alias=AliasChoices("equipment_reference", "equipment_name", "equipment"),
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

    @field_validator("steps", mode="before")
    @classmethod
    def _normalize_steps(cls, value: Any) -> Any:
        return coerce_raw_list(value)

    @field_validator("procedure_type", mode="before")
    @classmethod
    def _normalize_procedure_type(cls, value: Any) -> Any:
        if value is None:
            return ProcedureType.UNKNOWN
        if isinstance(value, ProcedureType):
            return value
        normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return ProcedureType(normalized)
        except ValueError:
            return ProcedureType.UNKNOWN
