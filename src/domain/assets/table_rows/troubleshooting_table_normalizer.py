from __future__ import annotations

import re

from src.domain.assets.table_rows.normalized_table_rows import NormalizedTableRows
from src.domain.assets.table_rows.table_row_patterns import (
    looks_explicit_header_cell,
    normalize_cell,
)

_FIELD_ORDER = ("symptom", "cause", "remedy", "notes")
_FIELD_LABELS = {
    "symptom": "Symptom",
    "cause": "Cause",
    "remedy": "Remedy",
    "notes": "Notes",
}
_FIELD_MARKERS = {
    "symptom": ("fault", "problem", "symptom", "trouble", "warning"),
    "cause": ("cause", "probable cause", "possible cause", "reason"),
    "remedy": (
        "action",
        "corrective action",
        "measure",
        "possible remedies",
        "remedies",
        "remedy",
        "solution",
    ),
    "notes": ("comment", "comments", "note", "notes", "remark", "remarks"),
}


class TroubleshootingTableNormalizer:
    def normalize(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        chunk_type: str | None,
    ) -> NormalizedTableRows | None:
        if not self._should_normalize(
            table_category=table_category,
            chunk_type=chunk_type,
        ):
            return None

        if len(rows) < 2:
            return None

        header_indexes = self._header_indexes(rows[0])
        if not header_indexes:
            return None

        ordered_fields = [
            field
            for field in _FIELD_ORDER
            if any(mapped_field == field for mapped_field in header_indexes.values())
        ]
        if len(ordered_fields) < 2:
            return None

        normalized_rows: list[list[str]] = []
        for row in rows[1:]:
            parsed = self._parse_row(row=row, header_indexes=header_indexes)
            if parsed is None:
                continue
            normalized_rows.append([parsed.get(field, "") for field in ordered_fields])

        if not normalized_rows:
            return None

        return NormalizedTableRows(
            headers=[_FIELD_LABELS[field] for field in ordered_fields],
            rows=normalized_rows,
        )

    @staticmethod
    def _should_normalize(
        *,
        table_category: str | None,
        chunk_type: str | None,
    ) -> bool:
        normalized_category = (table_category or "").strip().lower()
        if normalized_category == "troubleshooting_table":
            return True
        return (chunk_type or "").strip().lower() == "troubleshooting"

    def _header_indexes(self, header_row: list[str]) -> dict[int, str]:
        normalized_headers = [normalize_cell(cell).casefold() for cell in header_row]
        if not any(looks_explicit_header_cell(cell) for cell in normalized_headers if cell):
            return {}

        header_indexes: dict[int, str] = {}
        for index, header in enumerate(normalized_headers):
            mapped_field = self._map_header(header)
            if mapped_field is not None:
                header_indexes[index] = mapped_field
        return header_indexes

    def _map_header(self, header: str) -> str | None:
        for field in _FIELD_ORDER:
            if any(self._contains_marker(header, marker) for marker in _FIELD_MARKERS[field]):
                return field
        return None

    @staticmethod
    def _contains_marker(header: str, marker: str) -> bool:
        """Word-boundary match, not plain substring containment - a bare
        substring check would let a short marker like "action" match
        inside an unrelated word like "reaction".
        """
        return re.search(rf"\b{re.escape(marker)}\b", header) is not None

    @staticmethod
    def _parse_row(
        *,
        row: list[str],
        header_indexes: dict[int, str],
    ) -> dict[str, str] | None:
        parsed: dict[str, str] = {}
        extras: list[str] = []
        for index, cell in enumerate(row):
            value = normalize_cell(cell)
            if not value:
                continue
            mapped_field = header_indexes.get(index)
            if mapped_field is None:
                extras.append(value)
                continue
            parsed[mapped_field] = value

        if extras:
            existing_notes = parsed.get("notes", "")
            parsed["notes"] = " | ".join(
                part for part in (existing_notes, *extras) if part
            )

        signal_fields = [
            field for field in ("symptom", "cause", "remedy") if parsed.get(field)
        ]
        if not signal_fields:
            return None
        return parsed
