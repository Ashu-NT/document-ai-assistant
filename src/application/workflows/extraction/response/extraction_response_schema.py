from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from src.application.workflows.common import coerce_confidence_score
from src.domain.extraction import ProcedureType
from src.domain.extraction.contact_point import ContactPointType
from src.domain.extraction.semantic_relationship import SemanticEntityType


def coerce_raw_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("list fields must be arrays")
    return value


class _ExtractionItemBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    @field_validator("confidence_score", mode="before", check_fields=False)
    @classmethod
    def _validate_confidence_score(cls, value: Any) -> Any:
        return coerce_confidence_score(
            value,
            normalize_percent_range=True,
            on_invalid="original",
        )


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


class SafetyWarningPayload(_ExtractionItemBase):
    warning_type: str | None = None
    message: str | None = None
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


class MaintenanceIntervalPayload(_ExtractionItemBase):
    interval: str | None = None
    component_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("component_name", "component"),
    )
    task_reference: str | None = None
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


class TroubleshootingEntryPayload(_ExtractionItemBase):
    symptom: str | None = None
    cause: str | None = None
    remedy: str | None = None
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
    contact_points: list[ContactPointPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("contact_points", "contacts", "contact_point_list"),
    )
    procedures: list[ProcedurePayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("procedures", "procedure_list"),
    )
    specifications: list[SpecificationPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("specifications", "specification_list"),
    )
    safety_warnings: list[SafetyWarningPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("safety_warnings", "safety_warning_list"),
    )
    maintenance_intervals: list[MaintenanceIntervalPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("maintenance_intervals", "maintenance_interval_list"),
    )
    troubleshooting_entries: list[TroubleshootingEntryPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("troubleshooting_entries", "troubleshooting_list"),
    )
    identifiers: list[IdentifierPayload] = Field(
        default_factory=list,
        validation_alias=AliasChoices("identifiers", "identifier_list"),
    )

    @field_validator("confidence_score", mode="before")
    @classmethod
    def _validate_confidence_score(cls, value: Any) -> Any:
        return coerce_confidence_score(
            value,
            normalize_percent_range=True,
            on_invalid="original",
        )

    @field_validator(
        "maintenance_tasks",
        "spare_parts",
        "equipment",
        "manufacturers",
        "suppliers",
        "contact_points",
        "procedures",
        "specifications",
        "safety_warnings",
        "maintenance_intervals",
        "troubleshooting_entries",
        "identifiers",
        mode="before",
    )
    @classmethod
    def _normalize_list_field(cls, value: Any) -> Any:
        return coerce_raw_list(value)


_EXTRACTION_RESPONSE_JSON_SCHEMA = ExtractionResponsePayload.model_json_schema()


def build_extraction_response_json_schema() -> dict[str, Any]:
    return _EXTRACTION_RESPONSE_JSON_SCHEMA
