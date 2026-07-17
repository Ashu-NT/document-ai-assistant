from __future__ import annotations

from src.application.workflows.parsing.tables.structure.table_header_text_normalizer import (
    normalize_table_header_text,
)

_HEADER_LABEL_ALIASES: tuple[tuple[frozenset[str], str], ...] = (
    (frozenset({"part no", "part no.", "part nr", "part number"}), "part no"),
    (frozenset({"qty", "quantity"}), "quantity"),
    (frozenset({"designation", "desc", "description"}), "description"),
    (frozenset({"remark", "remarks", "comment", "comments", "note", "notes"}), "notes"),
    (frozenset({"ref", "reference"}), "reference"),
    (
        frozenset({"serial no", "serial no.", "serial nr", "serial number"}),
        "serial number",
    ),
)


class TableHeaderLabelCanonicalizer:
    def canonicalize(self, value: str | None) -> str:
        normalized = normalize_table_header_text(value)
        if not normalized:
            return ""
        for variants, canonical in _HEADER_LABEL_ALIASES:
            if normalized in variants:
                return canonical
        return normalized
