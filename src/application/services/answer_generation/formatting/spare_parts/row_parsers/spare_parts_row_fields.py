from __future__ import annotations

# This is a *catalog* of column labels seen across several unrelated
# spare-parts table conventions (generic part/position tables, P&ID/valve
# lists, exploded-view diagrams). It intentionally does not encode anything
# about any single document -- new synonyms can be appended without changing
# the parsing logic that consumes it.
ROW_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "position": (
        "part pos.",
        "part pos",
        "pos.",
        "pos",
        "position",
        "position no",
        "position no.",
        "pos nr",
        "pos nr.",
        "item",
        "item no",
        "item no.",
    ),
    "pid_position": (
        "p&id pos nr",
        "p&id pos nr.",
        "p&id position",
        "p&id",
        "tag",
    ),
    "quantity": ("qty", "quantity"),
    "unit": ("unit",),
    "service": ("service", "service function", "function"),
    "type": ("type",),
    "description": ("designation", "description", "denomination"),
    "part_no": (
        "part no",
        "part no.",
        "part number",
        "spare part no",
        "spare part no.",
        "article no",
        "article no.",
        "order no",
        "order no.",
        "material no",
        "material no.",
    ),
    "service_package": (
        "included in service package",
        "service package",
    ),
}
# Fields that make a row worth showing on their own. Position/quantity/unit
# alone are not "content" -- they are metadata about a row whose subject
# (what the part actually is) is still unknown.
CONTENT_FIELDS = ("description", "service", "type", "part_no", "pid_position")


def has_identifying_content(row: dict[str, str]) -> bool:
    for field_key in CONTENT_FIELDS:
        value = row.get(field_key)
        if value and value.strip():
            return True
    return False
