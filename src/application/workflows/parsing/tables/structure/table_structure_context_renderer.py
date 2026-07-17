from __future__ import annotations

from src.application.workflows.parsing.tables.structure.table_shape_resolver import (
    TableShapeResolver,
)
from src.application.workflows.shared.parallel_table_stream_view_resolver import (
    ParallelTableStreamView,
    ParallelTableStreamViewResolver,
)
from src.domain.assets import TableAsset


class TableStructureContextRenderer:
    def __init__(
        self,
        table_shape_resolver: TableShapeResolver | None = None,
        stream_view_resolver: ParallelTableStreamViewResolver | None = None,
    ) -> None:
        self.table_shape_resolver = table_shape_resolver or TableShapeResolver()
        self.stream_view_resolver = stream_view_resolver or ParallelTableStreamViewResolver()

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
        stream_views = self.stream_view_resolver.build(table)
        if stream_views:
            details = f"Parallel streams: {len(stream_views)}"
            if table.local_reading_order:
                details += f" ({table.local_reading_order})"
            parts.append(details)
            for stream_view in stream_views:
                summary = self._stream_summary(stream_view)
                if summary:
                    parts.append(summary)
        return "\n".join(parts) if parts else None

    @staticmethod
    def _stream_summary(stream_view: ParallelTableStreamView) -> str | None:
        descriptor = stream_view.descriptor
        if descriptor is None:
            return f"{stream_view.short_label} stream"
        details = [f"{stream_view.short_label} stream"]
        if descriptor.page_number is not None:
            details.append(f"page={descriptor.page_number}")
        if descriptor.row_count > 0:
            details.append(f"rows={descriptor.row_count}")
        if descriptor.column_count > 0:
            details.append(f"columns={descriptor.column_count}")
        return ", ".join(details)
