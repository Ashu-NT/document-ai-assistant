from __future__ import annotations

from src.application.workflows.extraction.batching.table_payload.table_payload_support import (
    TablePayloadSupport,
)
from src.domain.assets import TableAsset
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)


class SpecificationMatrixPayloadBuilder:
    def __init__(
        self,
        *,
        support: TablePayloadSupport | None = None,
    ) -> None:
        self.support = support or TablePayloadSupport()

    def build(self, table: TableAsset, *, chunk_type: str | None = None) -> str | None:
        if table.resolved_table_shape() != "specification_matrix":
            return None

        cleaned_rows = self.support.cleaned_rows(table)
        if len(cleaned_rows) < 2:
            return None

        headers = self.support.resolve_headers(cleaned_rows, table.header_paths)
        lines: list[str] = []
        for row_index, row in enumerate(cleaned_rows[1:], start=1):
            rendered_fields = [
                f"{headers[index]}={normalize_cell(cell)}"
                for index, cell in enumerate(row)
                if index < len(headers)
                and normalize_cell(headers[index])
                and normalize_cell(cell)
            ]
            if rendered_fields:
                lines.append(f"Row {row_index}: " + " | ".join(rendered_fields))

        if not lines:
            return None
        return "Structured specification records:\n" + "\n".join(lines)
