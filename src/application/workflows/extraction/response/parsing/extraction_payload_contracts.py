from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionPayloadContract:
    content_keys: tuple[str, ...]
    required_field_groups: tuple[tuple[str, ...], ...] = ()


EXTRACTION_PAYLOAD_CONTRACTS: dict[str, ExtractionPayloadContract] = {
    "maintenance_tasks": ExtractionPayloadContract(
        content_keys=(
            "title",
            "task",
            "name",
            "description",
            "details",
            "interval",
            "frequency",
            "component_name",
            "component",
            "equipment_id",
        ),
        required_field_groups=(("title", "task", "name"),),
    ),
    "spare_parts": ExtractionPayloadContract(
        content_keys=(
            "part_number",
            "part",
            "description",
            "quantity",
            "qty",
            "component_name",
            "component",
            "manufacturer_name",
            "manufacturer",
        ),
    ),
    "equipment": ExtractionPayloadContract(
        content_keys=(
            "name",
            "equipment_name",
            "model_number",
            "model",
            "serial_number",
            "serial",
            "manufacturer_name",
            "manufacturer",
        ),
    ),
    "manufacturers": ExtractionPayloadContract(
        content_keys=(
            "name",
            "manufacturer_name",
            "website",
            "url",
            "country",
        ),
        required_field_groups=(("name", "manufacturer_name"),),
    ),
    "suppliers": ExtractionPayloadContract(
        content_keys=(
            "name",
            "supplier_name",
            "website",
            "url",
            "country",
        ),
        required_field_groups=(("name", "supplier_name"),),
    ),
    "contact_points": ExtractionPayloadContract(
        content_keys=(
            "contact_type",
            "type",
            "value",
            "label",
            "owner_name",
            "owner_entity_type",
        ),
        required_field_groups=(("value",),),
    ),
    "procedures": ExtractionPayloadContract(
        content_keys=(
            "title",
            "steps",
            "component_name",
            "component",
        ),
        required_field_groups=(("title",),),
    ),
    "specifications": ExtractionPayloadContract(
        content_keys=(
            "parameter",
            "value",
            "unit",
            "component_name",
            "component",
        ),
        required_field_groups=(("parameter",), ("value",)),
    ),
    "safety_warnings": ExtractionPayloadContract(
        content_keys=(
            "warning_type",
            "message",
            "component_name",
            "component",
        ),
        required_field_groups=(("message",),),
    ),
    "maintenance_intervals": ExtractionPayloadContract(
        content_keys=(
            "interval",
            "component_name",
            "component",
            "task_reference",
        ),
        required_field_groups=(("interval",),),
    ),
    "troubleshooting_entries": ExtractionPayloadContract(
        content_keys=(
            "symptom",
            "cause",
            "remedy",
            "component_name",
            "component",
        ),
        required_field_groups=(("symptom",),),
    ),
    "identifiers": ExtractionPayloadContract(
        content_keys=(
            "raw_value",
            "value",
            "identifier_type",
            "type",
        ),
        required_field_groups=(("raw_value", "value"),),
    ),
}
