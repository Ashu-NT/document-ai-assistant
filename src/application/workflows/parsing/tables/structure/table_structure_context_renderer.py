from __future__ import annotations

from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
    TableShapeResolver,
)
from src.domain.assets import TableAsset


class TableStructureContextRenderer:
    def __init__(self, table_shape_resolver: TableShapeResolver | None = None) -> None:
        self.table_shape_resolver = table_shape_resolver or TableShapeResolver()

    def render(self, table: TableAsset) -> str | None:
        parts: list[str] = []
        table_shape = self.table_shape_resolver.resolve(table)
        if table_shape:
            parts.append(f"Table shape: {table_shape}")
        if table.header_paths:
            formatted_paths = [
                " > ".join(path).strip()
                for path in table.header_paths
                if any(str(part).strip() for part in path)
            ]
            if formatted_paths:
                parts.append("Header paths: " + " | ".join(formatted_paths))
        if table.axis_summary:
            parts.append(
                "Axis summary: "
                + "; ".join(
                    f"{key}={value}"
                    for key, value in table.axis_summary.items()
                    if str(key).strip() and str(value).strip()
                )
            )
        if table.parallel_stream_rows:
            details = f"Parallel streams: {len(table.parallel_stream_rows)}"
            if table.local_reading_order:
                details += f" ({table.local_reading_order})"
            parts.append(details)
        return "\n".join(parts) if parts else None
