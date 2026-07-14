from __future__ import annotations

from src.application.workflows.extraction.batching.table_payload.table_payload_support import (
    TablePayloadSupport,
)
from src.domain.assets import TableAsset
from src.domain.assets.table_rows.table_row_patterns import (
    active_interval_labels,
    looks_interval_header,
    normalize_cell,
)


class MaintenanceSchedulePayloadBuilder:
    def __init__(
        self,
        *,
        support: TablePayloadSupport | None = None,
    ) -> None:
        self.support = support or TablePayloadSupport()

    def build(self, table: TableAsset, *, chunk_type: str | None = None) -> str | None:
        if table.resolved_table_shape() != "maintenance_schedule_matrix":
            return None

        cleaned_rows = self.support.cleaned_rows(table)
        if len(cleaned_rows) < 2:
            return None

        headers = self.support.resolve_headers(cleaned_rows, table.header_paths)
        interval_indexes = {
            index for index, header in enumerate(headers) if looks_interval_header(header)
        }
        if len(interval_indexes) < 2:
            return None

        descriptive_indexes = [
            index for index in range(len(headers)) if index not in interval_indexes
        ]
        lines: list[str] = []
        for row_index, row in enumerate(cleaned_rows[1:], start=1):
            active_intervals = active_interval_labels(headers, row)
            descriptive_fields = [
                f"{headers[index]}={normalize_cell(row[index])}"
                for index in descriptive_indexes
                if index < len(row)
                and normalize_cell(headers[index])
                and normalize_cell(row[index])
            ]
            if not active_intervals and not descriptive_fields:
                continue

            rendered_fields = list(descriptive_fields)
            if active_intervals:
                rendered_fields.append(
                    "Intervals=" + ", ".join(active_intervals)
                )
            lines.append(f"Row {row_index}: " + " | ".join(rendered_fields))

        if not lines:
            return None
        return "Structured maintenance schedule:\n" + "\n".join(lines)
