"""Per-entity-type identity/dedup key functions.

These are copy-derived, field-for-field, from the REAL production mergers
under `src/application/workflows/extraction/response/merging/` (verified by
direct inspection, never guessed - see the Phase 2B research report). Golden
matching must use the SAME identity semantics production dedup already uses,
so a golden-truth match means the same thing a production merge decision
would mean.

Each function takes a plain `dict[str, str | None]` of an entity's raw
field values (works for both an expectation's `expected_fields` and an
actual domain entity's extracted fields - see `extraction_field_extraction.py`)
and returns a normalized identity tuple.
"""

from collections.abc import Callable, Mapping

from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)
from src.application.workflows.extraction.response.merging.merge_support import (
    normalize_for_dedup_key as _norm,
)

_IdentityKeyFunction = Callable[[Mapping[str, str | None]], tuple[str, ...]]


def _get(fields: Mapping[str, str | None], name: str) -> str | None:
    return fields.get(name)


def _maintenance_task_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # task_merger.py: (title, interval, component_name or equipment_id)
    return (
        _norm(_get(fields, "title")),
        _norm(_get(fields, "interval")),
        _norm(_get(fields, "component_name") or _get(fields, "equipment_id")),
    )


def _spare_part_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # spare_part_merger.py: (part_number or description, manufacturer_name, component_name)
    return (
        _norm(_get(fields, "part_number") or _get(fields, "description")),
        _norm(_get(fields, "manufacturer_name")),
        _norm(_get(fields, "component_name")),
    )


def _equipment_info_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # equipment_merger.py: (name, model_number, serial_number, manufacturer_name)
    return (
        _norm(_get(fields, "name")),
        _norm(_get(fields, "model_number")),
        _norm(_get(fields, "serial_number")),
        _norm(_get(fields, "manufacturer_name")),
    )


def _manufacturer_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # manufacturer_merger.py: name only
    return (_norm(_get(fields, "name")),)


def _supplier_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # supplier_merger.py: name only
    return (_norm(_get(fields, "name")),)


def _contact_point_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # contact_point_merger.py: (value, owner_name, owner_entity_type, contact_type)
    return (
        _norm(_get(fields, "value")),
        _norm(_get(fields, "owner_name")),
        _norm(_get(fields, "owner_entity_type")),
        _norm(_get(fields, "contact_type")),
    )


def _procedure_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # procedure_merger.py: (title, component_name)
    return (
        _norm(_get(fields, "title")),
        _norm(_get(fields, "component_name")),
    )


def _specification_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # specification_merger.py: (parameter, component_name)
    return (
        _norm(_get(fields, "parameter")),
        _norm(_get(fields, "component_name")),
    )


def _safety_warning_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # safety_warning_merger.py: message only
    return (_norm(_get(fields, "message")),)


def _maintenance_interval_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # maintenance_interval_merger.py: (interval, component_name)
    return (
        _norm(_get(fields, "interval")),
        _norm(_get(fields, "component_name")),
    )


def _troubleshooting_entry_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # troubleshooting_entry_merger.py: (symptom, component_name)
    return (
        _norm(_get(fields, "symptom")),
        _norm(_get(fields, "component_name")),
    )


def _extracted_identifier_key(fields: Mapping[str, str | None]) -> tuple[str, ...]:
    # identifier_merger.py: (raw_value, identifier_type)
    return (
        _norm(_get(fields, "raw_value")),
        _norm(_get(fields, "identifier_type")),
    )


ENTITY_IDENTITY_KEY_FUNCTIONS: dict[ExtractionEntityType, _IdentityKeyFunction] = {
    ExtractionEntityType.MAINTENANCE_TASK: _maintenance_task_key,
    ExtractionEntityType.SPARE_PART: _spare_part_key,
    ExtractionEntityType.EQUIPMENT_INFO: _equipment_info_key,
    ExtractionEntityType.MANUFACTURER: _manufacturer_key,
    ExtractionEntityType.SUPPLIER: _supplier_key,
    ExtractionEntityType.CONTACT_POINT: _contact_point_key,
    ExtractionEntityType.PROCEDURE: _procedure_key,
    ExtractionEntityType.SPECIFICATION: _specification_key,
    ExtractionEntityType.SAFETY_WARNING: _safety_warning_key,
    ExtractionEntityType.MAINTENANCE_INTERVAL: _maintenance_interval_key,
    ExtractionEntityType.TROUBLESHOOTING_ENTRY: _troubleshooting_entry_key,
    ExtractionEntityType.EXTRACTED_IDENTIFIER: _extracted_identifier_key,
}

# The named fields each identity key function reads, in the same order the
# tuple is built - used only for diagnostics (which fields were "the
# identity" for a given match/mismatch report).
ENTITY_IDENTITY_FIELD_NAMES: dict[ExtractionEntityType, tuple[str, ...]] = {
    ExtractionEntityType.MAINTENANCE_TASK: ("title", "interval", "component_name"),
    ExtractionEntityType.SPARE_PART: (
        "part_number",
        "manufacturer_name",
        "component_name",
    ),
    ExtractionEntityType.EQUIPMENT_INFO: (
        "name",
        "model_number",
        "serial_number",
        "manufacturer_name",
    ),
    ExtractionEntityType.MANUFACTURER: ("name",),
    ExtractionEntityType.SUPPLIER: ("name",),
    ExtractionEntityType.CONTACT_POINT: (
        "value",
        "owner_name",
        "owner_entity_type",
        "contact_type",
    ),
    ExtractionEntityType.PROCEDURE: ("title", "component_name"),
    ExtractionEntityType.SPECIFICATION: ("parameter", "component_name"),
    ExtractionEntityType.SAFETY_WARNING: ("message",),
    ExtractionEntityType.MAINTENANCE_INTERVAL: ("interval", "component_name"),
    ExtractionEntityType.TROUBLESHOOTING_ENTRY: ("symptom", "component_name"),
    ExtractionEntityType.EXTRACTED_IDENTIFIER: ("raw_value", "identifier_type"),
}


def compute_identity_key(
    entity_type: ExtractionEntityType,
    fields: Mapping[str, str | None],
    *,
    override_field_names: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    if override_field_names is not None:
        return tuple(_norm(fields.get(name)) for name in override_field_names)
    return ENTITY_IDENTITY_KEY_FUNCTIONS[entity_type](fields)


__all__ = [
    "ENTITY_IDENTITY_KEY_FUNCTIONS",
    "ENTITY_IDENTITY_FIELD_NAMES",
    "compute_identity_key",
]
