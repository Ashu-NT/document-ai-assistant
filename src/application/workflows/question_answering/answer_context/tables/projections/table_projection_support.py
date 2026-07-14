from __future__ import annotations

from src.domain.assets.table_rows.table_row_patterns import (
    dedupe_headers,
    normalize_cell,
)


class TableProjectionSupport:
    @staticmethod
    def resolve_headers(
        cleaned_rows: list[list[str]],
        header_paths: list[list[str]],
    ) -> list[str]:
        if not cleaned_rows:
            return []

        row_headers = dedupe_headers(cleaned_rows[0])
        width = max(len(row_headers), len(header_paths))
        resolved: list[str] = []
        for index in range(width):
            path = header_paths[index] if index < len(header_paths) else []
            path_label = TableProjectionSupport._path_label(path)
            row_header = row_headers[index] if index < len(row_headers) else ""
            resolved.append(path_label or normalize_cell(row_header))
        return dedupe_headers(resolved)

    @staticmethod
    def combine_value_with_unit(
        value: str | None,
        unit: str | None,
    ) -> str | None:
        cleaned_value = normalize_cell(value)
        cleaned_unit = normalize_cell(unit)
        if not cleaned_value:
            return None
        if not cleaned_unit:
            return cleaned_value
        lowered_value = cleaned_value.casefold()
        lowered_unit = cleaned_unit.casefold()
        if lowered_unit in lowered_value:
            return cleaned_value
        return f"{cleaned_value} {cleaned_unit}"

    @staticmethod
    def _path_label(path: list[str]) -> str:
        cleaned = [normalize_cell(part) for part in path if normalize_cell(part)]
        if not cleaned:
            return ""
        return cleaned[-1]
