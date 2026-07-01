from __future__ import annotations

import ast
import json
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


def _try_yaml_load(candidate: str) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise TypeError("yaml is not installed") from exc

    try:
        return yaml.safe_load(candidate)
    except Exception as exc:
        raise TypeError("yaml parsing failed") from exc


def coerce_raw_list(value: Any) -> Any:
    """Best-effort coercion of a raw field value into a list before validation.

    Handles the model returning a JSON/YAML/Python-literal-encoded string
    instead of an actual array, and wraps a bare object in a single-item list.
    Does not filter or validate items — that is the schema's job.
    """
    if value is None:
        return None

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        for loader in (json.loads, ast.literal_eval, _try_yaml_load):
            try:
                value = loader(stripped)
                break
            except (json.JSONDecodeError, SyntaxError, ValueError, TypeError):
                continue

    if isinstance(value, dict):
        return [value]

    return value


def _drop_null_items(value: Any) -> Any:
    if isinstance(value, list):
        return [item for item in value if item is not None]
    return value


def _coerce_confidence(value: Any) -> Any:
    """Allow percentage strings (e.g. "90%") before Pydantic's numeric coercion."""
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
    title: str | None = Field(default=None, validation_alias=AliasChoices("title", "task", "name"))
    description: str | None = Field(default=None, validation_alias=AliasChoices("description", "details"))
    interval: str | None = Field(default=None, validation_alias=AliasChoices("interval", "frequency"))
    component_name: str | None = Field(default=None, validation_alias=AliasChoices("component_name", "component"))
    equipment_id: str | None = None
    source_chunk_id: str | None = Field(default=None, validation_alias=AliasChoices("source_chunk_id", "chunk_id"))
    confidence_score: float | None = Field(default=None, validation_alias=AliasChoices("confidence_score", "confidence"))
    requires_human_review: bool | None = Field(
        default=None, validation_alias=AliasChoices("requires_human_review", "requires_review")
    )


class SparePartPayload(_ExtractionItemBase):
    part_number: str | None = Field(default=None, validation_alias=AliasChoices("part_number", "part"))
    description: str | None = None
    quantity: str | None = Field(default=None, validation_alias=AliasChoices("quantity", "qty"))
    component_name: str | None = Field(default=None, validation_alias=AliasChoices("component_name", "component"))
    manufacturer_name: str | None = Field(
        default=None, validation_alias=AliasChoices("manufacturer_name", "manufacturer")
    )
    source_chunk_id: str | None = Field(default=None, validation_alias=AliasChoices("source_chunk_id", "chunk_id"))
    confidence_score: float | None = Field(default=None, validation_alias=AliasChoices("confidence_score", "confidence"))
    requires_human_review: bool | None = Field(
        default=None, validation_alias=AliasChoices("requires_human_review", "requires_review")
    )


class EquipmentPayload(_ExtractionItemBase):
    name: str | None = Field(default=None, validation_alias=AliasChoices("name", "equipment_name"))
    model_number: str | None = Field(default=None, validation_alias=AliasChoices("model_number", "model"))
    serial_number: str | None = Field(default=None, validation_alias=AliasChoices("serial_number", "serial"))
    manufacturer_name: str | None = Field(
        default=None, validation_alias=AliasChoices("manufacturer_name", "manufacturer")
    )
    source_chunk_id: str | None = Field(default=None, validation_alias=AliasChoices("source_chunk_id", "chunk_id"))
    confidence_score: float | None = Field(default=None, validation_alias=AliasChoices("confidence_score", "confidence"))
    requires_human_review: bool | None = Field(
        default=None, validation_alias=AliasChoices("requires_human_review", "requires_review")
    )


class ManufacturerPayload(_ExtractionItemBase):
    name: str | None = Field(default=None, validation_alias=AliasChoices("name", "manufacturer_name"))
    website: str | None = Field(default=None, validation_alias=AliasChoices("website", "url"))
    country: str | None = None
    source_chunk_id: str | None = Field(default=None, validation_alias=AliasChoices("source_chunk_id", "chunk_id"))
    confidence_score: float | None = Field(default=None, validation_alias=AliasChoices("confidence_score", "confidence"))
    requires_human_review: bool | None = Field(
        default=None, validation_alias=AliasChoices("requires_human_review", "requires_review")
    )


class IdentifierPayload(_ExtractionItemBase):
    raw_value: str | None = Field(default=None, validation_alias=AliasChoices("raw_value", "value"))
    identifier_type: str | None = Field(default=None, validation_alias=AliasChoices("identifier_type", "type"))
    source_chunk_id: str | None = Field(default=None, validation_alias=AliasChoices("source_chunk_id", "chunk_id"))
    confidence_score: float | None = Field(default=None, validation_alias=AliasChoices("confidence_score", "confidence"))
    requires_human_review: bool | None = Field(
        default=None, validation_alias=AliasChoices("requires_human_review", "requires_review")
    )


class ExtractionResponsePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    confidence_score: float | None = Field(
        default=None, validation_alias=AliasChoices("confidence_score", "confidence", "overall_confidence")
    )
    requires_human_review: bool | None = Field(
        default=None, validation_alias=AliasChoices("requires_human_review", "requires_review")
    )
    maintenance_tasks: list[MaintenanceTaskPayload] = Field(
        default_factory=list, validation_alias=AliasChoices("maintenance_tasks", "tasks")
    )
    spare_parts: list[SparePartPayload] = Field(
        default_factory=list, validation_alias=AliasChoices("spare_parts", "parts")
    )
    equipment: list[EquipmentPayload] = Field(
        default_factory=list, validation_alias=AliasChoices("equipment", "equipment_info")
    )
    manufacturers: list[ManufacturerPayload] = Field(
        default_factory=list, validation_alias=AliasChoices("manufacturers", "manufacturer_list")
    )
    identifiers: list[IdentifierPayload] = Field(
        default_factory=list, validation_alias=AliasChoices("identifiers", "identifier_list")
    )

    @field_validator("confidence_score", mode="before")
    @classmethod
    def _validate_confidence_score(cls, value: Any) -> Any:
        return _coerce_confidence(value)

    @field_validator(
        "maintenance_tasks", "spare_parts", "equipment", "manufacturers", "identifiers", mode="before"
    )
    @classmethod
    def _normalize_list_field(cls, value: Any) -> Any:
        coerced = coerce_raw_list(value)
        if coerced is None:
            return []
        return _drop_null_items(coerced)


_EXTRACTION_RESPONSE_JSON_SCHEMA = ExtractionResponsePayload.model_json_schema()


def build_extraction_response_json_schema() -> dict[str, Any]:
    return _EXTRACTION_RESPONSE_JSON_SCHEMA
