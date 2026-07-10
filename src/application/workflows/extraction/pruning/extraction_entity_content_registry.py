from __future__ import annotations

from src.domain.extraction import (
    ContactPoint,
    EquipmentInfo,
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

# Per-entity "content" fields: the fields that actually carry extracted
# information, as opposed to bookkeeping (id/document_id/source_chunk_id/
# source/source_metadata/confidence_score/requires_human_review/audit,
# which every entity always has populated regardless of whether anything
# real was extracted) or a classification field that always defaults to a
# non-null placeholder (SafetyWarning.warning_type defaults to "warning",
# Procedure.procedure_type defaults to UNKNOWN -- neither is evidence the
# LLM found real information, so neither counts as content here).
#
# Used as a final, entity-type-agnostic safety net right before saving: an
# extracted item can pass its per-field required-text checks during
# construction (e.g. by getting a non-empty single field) and still be
# effectively empty overall, or reach this point empty through some other
# path this per-field checking doesn't cover. Whatever the cause, an item
# with every content field null/empty apart from document_id/
# source_chunk_id must never be persisted.
ENTITY_CONTENT_FIELDS: dict[type, tuple[str, ...]] = {
    MaintenanceTask: ("title", "description", "interval", "component_name", "equipment_id"),
    SparePart: ("part_number", "description", "quantity", "component_name", "manufacturer_name"),
    EquipmentInfo: ("name", "model_number", "serial_number", "manufacturer_name"),
    Manufacturer: ("name", "website", "country"),
    Supplier: ("name", "website", "country"),
    ContactPoint: ("value", "label", "owner_name"),
    Procedure: ("title", "steps", "component_name", "equipment_id"),
    Specification: ("parameter", "value", "unit", "component_name"),
    SafetyWarning: ("message", "component_name"),
    MaintenanceInterval: ("interval", "component_name", "maintenance_task_id"),
    TroubleshootingEntry: ("symptom", "cause", "remedy", "component_name", "equipment_id"),
}
