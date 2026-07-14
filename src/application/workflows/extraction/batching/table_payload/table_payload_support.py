from __future__ import annotations

from src.domain.assets import TableAsset
from src.domain.assets.table_rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.domain.assets.table_rows.table_row_patterns import (
    dedupe_headers,
    normalize_cell,
)


class TablePayloadSupport:
    def __init__(
        self,
        *,
        row_canonicalizer: TableRowCanonicalizer | None = None,
    ) -> None:
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()

    def cleaned_rows(self, table: TableAsset) -> list[list[str]]:
        return self.row_canonicalizer.canonicalize(table.rows)

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
            path_label = TablePayloadSupport._path_label(path)
            row_header = row_headers[index] if index < len(row_headers) else ""
            resolved.append(path_label or normalize_cell(row_header))
        return dedupe_headers(resolved)

    @staticmethod
    def render_fields(
        headers: list[str],
        row: list[str],
    ) -> list[str]:
        rendered: list[str] = []
        for index, cell in enumerate(row):
            if index >= len(headers):
                continue
            header = normalize_cell(headers[index])
            value = normalize_cell(cell)
            if not header or not value:
                continue
            rendered.append(f"{header}={value}")
        return rendered

    @staticmethod
    def _path_label(path: list[str]) -> str:
        cleaned = [normalize_cell(part) for part in path if normalize_cell(part)]
        if not cleaned:
            return ""
        return cleaned[-1]
