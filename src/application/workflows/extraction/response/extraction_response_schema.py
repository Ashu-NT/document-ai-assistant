from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.response.schemas import (
    ContactPointPayload,
    EquipmentPayload,
    ExtractionResponsePayload,
    IdentifierPayload,
    MaintenanceIntervalPayload,
    MaintenanceTaskPayload,
    ManufacturerPayload,
    ProcedurePayload,
    SafetyWarningPayload,
    SparePartPayload,
    SpecificationPayload,
    SupplierPayload,
    TroubleshootingEntryPayload,
    _ExtractionItemBase,
    coerce_raw_list,
)

__all__ = [
    "coerce_raw_list",
    "_ExtractionItemBase",
    "MaintenanceTaskPayload",
    "SparePartPayload",
    "EquipmentPayload",
    "ManufacturerPayload",
    "SupplierPayload",
    "ContactPointPayload",
    "ProcedurePayload",
    "SpecificationPayload",
    "SafetyWarningPayload",
    "MaintenanceIntervalPayload",
    "TroubleshootingEntryPayload",
    "IdentifierPayload",
    "ExtractionResponsePayload",
    "build_extraction_response_json_schema",
]

_EXTRACTION_RESPONSE_JSON_SCHEMA = ExtractionResponsePayload.model_json_schema()


def build_extraction_response_json_schema() -> dict[str, Any]:
    return _EXTRACTION_RESPONSE_JSON_SCHEMA
