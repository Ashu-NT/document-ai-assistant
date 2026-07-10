from __future__ import annotations

from typing import Any

from src.application.workflows.extraction.pruning.extraction_entity_content_registry import (
    ENTITY_CONTENT_FIELDS,
)
from src.domain.extraction import (
    ContactPoint,
    EquipmentInfo,
    ExtractionResult,
    MaintenanceInterval,
    MaintenanceTask,
    Manufacturer,
    Procedure,
    SafetyWarning,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
)


def has_meaningful_entity_content(
    entity: Any,
    content_fields: tuple[str, ...],
) -> bool:
    for field_name in content_fields:
        value = getattr(entity, field_name, None)
        if isinstance(value, str):
            if value.strip():
                return True
        elif isinstance(value, list):
            if value:
                return True
        elif value is not None:
            return True
    return False


def keep_non_empty(entities: list[Any], entity_type: type) -> list[Any]:
    content_fields = ENTITY_CONTENT_FIELDS[entity_type]
    return [
        entity
        for entity in entities
        if has_meaningful_entity_content(entity, content_fields)
    ]


def drop_empty_entities(
    extraction_result: ExtractionResult,
) -> tuple[ExtractionResult, int]:
    """Final safety net, run right before validation/save: drops any
    extracted entity whose content fields are all null/empty, no matter
    how it reached this point. See ENTITY_CONTENT_FIELDS for what counts
    as content per entity type. Returns the result and how many items
    were dropped, for progress reporting."""
    field_lists = [
        ("maintenance_tasks", MaintenanceTask),
        ("spare_parts", SparePart),
        ("equipment", EquipmentInfo),
        ("manufacturers", Manufacturer),
        ("suppliers", Supplier),
        ("contact_points", ContactPoint),
        ("procedures", Procedure),
        ("specifications", Specification),
        ("safety_warnings", SafetyWarning),
        ("maintenance_intervals", MaintenanceInterval),
        ("troubleshooting_entries", TroubleshootingEntry),
    ]
    dropped_count = 0
    for attribute_name, entity_type in field_lists:
        original = getattr(extraction_result, attribute_name)
        kept = keep_non_empty(original, entity_type)
        dropped_count += len(original) - len(kept)
        setattr(extraction_result, attribute_name, kept)
    return extraction_result, dropped_count
