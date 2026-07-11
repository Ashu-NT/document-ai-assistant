from __future__ import annotations

from collections.abc import Mapping

STRUCTURED_ENTITY_FIELD_LABELS: dict[str, tuple[tuple[str, str], ...]] = {
    "manufacturer": (
        ("name", "Manufacturer Name"),
        ("website", "Manufacturer Website"),
        ("country", "Manufacturer Country"),
    ),
    "supplier": (
        ("name", "Supplier Name"),
        ("website", "Supplier Website"),
        ("country", "Supplier Country"),
    ),
    "spare_part": (
        ("part_number", "Part Number"),
        ("description", "Part Description"),
        ("quantity", "Part Quantity"),
        ("component_name", "Part Component"),
    ),
    "equipment": (
        ("name", "Equipment Name"),
        ("model_number", "Equipment Model Number"),
        ("serial_number", "Equipment Serial Number"),
    ),
    "maintenance_task": (
        ("title", "Maintenance Task"),
        ("interval", "Maintenance Interval"),
        ("component_name", "Maintenance Component"),
    ),
    "contact_point": (
        ("owner_name", "Contact Owner"),
        ("label", "Contact Label"),
    ),
}


def field_labels_for_entity(
    entity_type: str,
    entity: Mapping[str, object],
) -> tuple[tuple[str, str], ...]:
    if entity_type != "contact_point":
        return STRUCTURED_ENTITY_FIELD_LABELS.get(entity_type, ())
    return (
        ("value", contact_value_label(entity)),
        *STRUCTURED_ENTITY_FIELD_LABELS["contact_point"],
    )


def contact_value_label(entity: Mapping[str, object]) -> str:
    owner_entity_type = str(entity.get("owner_entity_type") or "").strip().lower()
    owner_prefix = {
        "manufacturer": "Manufacturer",
        "supplier": "Supplier",
    }.get(owner_entity_type, "Contact")
    contact_type = str(entity.get("contact_type") or "").strip().lower()
    contact_suffix = {
        "phone_number": "Phone Number",
        "fax_number": "Fax Number",
        "email_address": "Email Address",
        "url": "Website",
    }.get(contact_type, "Value")
    return f"{owner_prefix} {contact_suffix}"
