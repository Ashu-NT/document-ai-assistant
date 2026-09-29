"""Extracts the semantic content fields (never id/document_id/source/
source_metadata/confidence/audit) from a real production entity dataclass
instance into a plain `dict[str, str | None]`, so the same matcher code path
that compares `expected_fields` (authored by a human) can compare an actual
extracted entity too. Field lists are the entity's real content fields, per
`src/domain/extraction/*.py` (see the Phase 2B research report, section 6).
"""

from collections.abc import Mapping
from typing import Any

from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)

_CONTENT_FIELD_NAMES: dict[ExtractionEntityType, tuple[str, ...]] = {
    ExtractionEntityType.MAINTENANCE_TASK: (
        "title",
        "description",
        "interval",
        "component_name",
        "equipment_id",
    ),
    ExtractionEntityType.SPARE_PART: (
        "part_number",
        "description",
        "quantity",
        "component_name",
        "manufacturer_name",
    ),
    ExtractionEntityType.EQUIPMENT_INFO: (
        "name",
        "model_number",
        "serial_number",
        "manufacturer_name",
    ),
    ExtractionEntityType.MANUFACTURER: ("name", "website", "country"),
    ExtractionEntityType.SUPPLIER: ("name", "website", "country"),
    ExtractionEntityType.CONTACT_POINT: (
        "contact_type",
        "value",
        "label",
        "owner_name",
        "owner_entity_type",
    ),
    ExtractionEntityType.PROCEDURE: (
        "title",
        "procedure_type",
        "steps",
        "component_name",
        "equipment_id",
    ),
    ExtractionEntityType.SPECIFICATION: ("parameter", "value", "unit", "component_name"),
    ExtractionEntityType.SAFETY_WARNING: ("warning_type", "message", "component_name"),
    ExtractionEntityType.MAINTENANCE_INTERVAL: (
        "interval",
        "component_name",
        "maintenance_task_id",
    ),
    ExtractionEntityType.TROUBLESHOOTING_ENTRY: (
        "symptom",
        "cause",
        "remedy",
        "component_name",
        "equipment_id",
    ),
    ExtractionEntityType.EXTRACTED_IDENTIFIER: ("raw_value", "identifier_type"),
}


def content_field_names(entity_type: ExtractionEntityType) -> tuple[str, ...]:
    return _CONTENT_FIELD_NAMES[entity_type]


def _stringify(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list | tuple):
        return " ".join(str(item) for item in value)
    # Enums (ContactPointType, ProcedureType, SemanticEntityType, ...):
    # use `.value` so normalization matches how a human would write the
    # fixture's plain string value.
    return getattr(value, "value", str(value))


def extract_actual_fields(
    entity: Any, entity_type: ExtractionEntityType
) -> dict[str, str | None]:
    return {
        name: _stringify(getattr(entity, name, None))
        for name in content_field_names(entity_type)
    }


def normalize_expected_fields(
    expected_fields: Mapping[str, str], entity_type: ExtractionEntityType
) -> dict[str, str | None]:
    """Fills in any content field the fixture didn't set with None, so
    comparisons always run over the full, entity-type-appropriate field
    set (missing == None, never a KeyError)."""
    return {
        name: expected_fields.get(name)
        for name in content_field_names(entity_type)
    }


__all__ = [
    "content_field_names",
    "extract_actual_fields",
    "normalize_expected_fields",
]
