from __future__ import annotations

from src.application.workflows.extraction.table_payload.table_payload_support import (
    TablePayloadSupport,
)
from src.application.workflows.extraction.table_windowing.table_evidence_window import (
    TableEvidenceWindow,
)
from src.domain.assets import TableAsset

# Generic, family-agnostic row-window builder. Operates directly on
# TableAsset.rows (structured list[list[str]], first row = header) and
# header_paths - the SAME structured metadata the existing per-shape
# payload builders (SpecificationMatrixPayloadBuilder, etc.) already use -
# never regex-parses Markdown. Row numbering matches the existing
# "Row N: Header=Value | ..." convention those builders already use for the
# FULL canonical table (1-based, relative to TablePayloadSupport's cleaned
# data rows), so a window's "Row 11" means the same logical row as "Row 11"
# in the full-table rendering.
#
# Deliberately produces exactly ONE compact rendering per window (no
# Markdown duplicate) - the diagnostic that motivated this experiment found
# the canonical hydrated chunk's existing rendering duplicates the same
# rows twice (compact + Markdown), roughly doubling evidence size for zero
# added information. That duplication is left untouched in the canonical
# hydration path (out of scope here); this builder simply does not repeat
# it in the new windowed view.


class TableEvidenceWindowBuilder:
    def __init__(
        self,
        *,
        rows_per_window: int,
        support: TablePayloadSupport | None = None,
    ) -> None:
        self.rows_per_window = max(1, rows_per_window)
        self.support = support or TablePayloadSupport()

    def should_window(self, table: TableAsset) -> bool:
        """True when this table has more data rows than fit in one window -
        a table at or under the threshold is left as a single, unwindowed
        call."""
        return self._data_row_count(table) > self.rows_per_window

    def build_windows(
        self,
        table: TableAsset,
        *,
        source_chunk_id: str,
    ) -> list[TableEvidenceWindow]:
        cleaned_rows = self.support.cleaned_rows(table)
        if len(cleaned_rows) < 2:
            return []

        data_rows = cleaned_rows[1:]
        headers = self.support.resolve_headers(cleaned_rows, table.header_paths)
        total_row_count = len(data_rows)

        row_slices = [
            data_rows[offset : offset + self.rows_per_window]
            for offset in range(0, total_row_count, self.rows_per_window)
        ]
        window_count = len(row_slices)

        windows: list[TableEvidenceWindow] = []
        for window_index, row_slice in enumerate(row_slices, start=1):
            row_start = (window_index - 1) * self.rows_per_window + 1
            row_end = row_start + len(row_slice) - 1
            rendered_text = self._render_window(
                headers,
                row_slice,
                row_start=row_start,
                row_end=row_end,
                total_row_count=total_row_count,
                window_index=window_index,
                window_count=window_count,
            )
            windows.append(
                TableEvidenceWindow(
                    source_chunk_id=source_chunk_id,
                    window_index=window_index,
                    window_count=window_count,
                    row_start=row_start,
                    row_end=row_end,
                    total_row_count=total_row_count,
                    rendered_text=rendered_text,
                )
            )
        return windows

    def _data_row_count(self, table: TableAsset) -> int:
        cleaned_rows = self.support.cleaned_rows(table)
        return max(0, len(cleaned_rows) - 1)

    @staticmethod
    def _render_window(
        headers: list[str],
        row_slice: list[list[str]],
        *,
        row_start: int,
        row_end: int,
        total_row_count: int,
        window_index: int,
        window_count: int,
    ) -> str:
        lines = [
            "Table header: " + " | ".join(header for header in headers if header),
            (
                f"This is window {window_index}/{window_count} of a larger table: "
                f"rows {row_start}-{row_end} of {total_row_count} total rows. "
                "Extract only from the rows shown below."
            ),
        ]
        for offset, row in enumerate(row_slice):
            row_number = row_start + offset
            fields = TablePayloadSupport.render_fields(headers, row)
            if fields:
                lines.append(f"Row {row_number}: " + " | ".join(fields))
        return "\n".join(lines)
