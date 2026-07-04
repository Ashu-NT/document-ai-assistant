from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


def coerce_raw_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("list fields must be arrays")
    return value


def _coerce_confidence(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip().strip('"').strip("'").strip()
        if stripped.endswith("%"):
            try:
                return float(stripped[:-1].strip()) / 100
            except ValueError:
                return value
    return value


class _ExtractionItemBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    @field_validator("confidence_score", mode="before", check_fields=False)
    @classmethod
    def _validate_confidence_score(cls, value: Any) -> Any:
        return _coerce_confidence(value)


class MaintenanceTaskPayload(_ExtractionItemBase):
    title: str | None = Field(
        default=None,
        validation_alias=AliasChoices("title", "task", "name"),
    )
    description: str | None = Field(
        default=None,
        validation_alias=AliasChoices("description", "details"),
    )
    interval: str | None = Field(
        default=None,
        validation_alias=AliasChoices("interval", "frequency"),
    )
    component_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("component_name", "component"),
    )
    equipment_id: str | None = None
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


class ExtractionResponsePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    confidence_score: float | None = Field(
        default=None,
        validation_alias=AliasChoices("confidence_score", "confidence", "overall_confidence"),
    )
    requires_human_review: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("requires_human_review", "requires_review"),
    )
    maintenance_tasks: list[MaintenanceTaskPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("maintenance_tasks", "tasks"),
    )
    spare_parts: list[SparePartPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("spare_parts", "parts"),
    )
    equipment: list[EquipmentPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("equipment", "equipment_info"),
    )
    manufacturers: list[ManufacturerPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("manufacturers", "manufacturer_list"),
    )
    suppliers: list[SupplierPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("suppliers", "supplier_list"),
    )
    identifiers: list[IdentifierPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("identifiers", "identifier_list"),
    )

    @field_validator("confidence_score", mode="before")
    @classmethod
    def _validate_confidence_score(cls, value: Any) -> Any:
        return _coerce_confidence(value)

    @field_validator(
        "maintenance_tasks",
        "spare_parts",
        "equipment",
        "manufacturers",
        "suppliers",
        "identifiers",
        mode="before",
    )
    @classmethod
    def _normalize_list_field(cls, value: Any) -> Any:
        return coerce_raw_list(value)


_EXTRACTION_RESPONSE_JSON_SCHEMA = ExtractionResponsePayload.model_json_schema()


def build_extraction_response_json_schema() -> dict[str, Any]:
    return _EXTRACTION_RESPONSE_JSON_SCHEMA
