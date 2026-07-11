from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from src.application.workflows.common.confidence_coercion import coerce_confidence_score
from src.application.workflows.extraction.response.schemas.contact_point_payload import (
    ContactPointPayload,
)
from src.application.workflows.extraction.response.schemas.equipment_payload import (
    EquipmentPayload,
)
from src.application.workflows.extraction.response.schemas.extraction_payload_base import (
    coerce_raw_list,
)
from src.application.workflows.extraction.response.schemas.identifier_payload import (
    IdentifierPayload,
)
from src.application.workflows.extraction.response.schemas.maintenance_interval_payload import (
    MaintenanceIntervalPayload,
)
from src.application.workflows.extraction.response.schemas.maintenance_task_payload import (
    MaintenanceTaskPayload,
)
from src.application.workflows.extraction.response.schemas.organization_entity_payload import (
    ManufacturerPayload,
    SupplierPayload,
)
from src.application.workflows.extraction.response.schemas.procedure_payload import (
    ProcedurePayload,
)
from src.application.workflows.extraction.response.schemas.safety_warning_payload import (
    SafetyWarningPayload,
)
from src.application.workflows.extraction.response.schemas.spare_part_payload import (
    SparePartPayload,
)
from src.application.workflows.extraction.response.schemas.specification_payload import (
    SpecificationPayload,
)
from src.application.workflows.extraction.response.schemas.troubleshooting_entry_payload import (
    TroubleshootingEntryPayload,
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
