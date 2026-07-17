from __future__ import annotations

import re

from src.domain.assets import TableAsset
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    looks_explicit_header_cell,
    looks_label_cell,
    looks_numeric,
    normalize_cell,
)


class TableHeaderPathBuilder:
    def build_paths(self, table: TableAsset) -> tuple[tuple[str, ...], ...]:
        if not table.rows:
            return ()

        header_row_count = self.resolve_header_row_count(table)
        column_count = max(
            table.column_count or 0,
            max((len(row) for row in table.rows), default=0),
        )
        raw_paths = tuple(
            self._path_for_column(
                table=table,
                column_index=column_index,
                header_row_count=header_row_count,
            )
            for column_index in range(column_count)
        )
        return tuple(path for path in raw_paths if path)

    def build_umbrella_collapsed_paths(
        self,
        table: TableAsset,
    ) -> tuple[tuple[str, ...], ...]:
        return self.collapse_uniform_umbrella(self.build_paths(table))

    def umbrella_text(self, table: TableAsset) -> str | None:
        if not table.rows:
            return None
        first_row = table.rows[0]
        if not self._looks_uniform_umbrella_row(first_row):
            return None
        label = self._uniform_row_label(first_row)
        return label or None

    def resolve_header_row_count(self, table: TableAsset) -> int:
        rows = table.rows
        if len(rows) <= 1:
            return 1

        header_row_count = 1
        max_rows = min(3, len(rows))
        if self._looks_uniform_umbrella_row(rows[0]) and self._looks_header_row(rows[1]):
            header_row_count = 2

        if any(span.row_start == 0 and span.col_span > 1 for span in table.cell_spans):
            header_row_count = max(header_row_count, 2)

        for row_index in range(1, max_rows):
            if row_index < header_row_count:
                continue
            if row_index >= len(rows) - 1:
                break
            if not self._has_structural_header_evidence(table, row_index):
                break
            header_row_count += 1

        return max(1, header_row_count)

    @staticmethod
    def _has_structural_header_evidence(table: TableAsset, row_index: int) -> bool:
        """Widening the header past what the umbrella/span checks above
        already established requires real merged-cell evidence for this
        specific row, not just "this row reads as text" - a table's own
        first data row (e.g. a maintenance task description, a
        troubleshooting symptom) reads just as textual/label-like as a
        genuine header row, so a text-only score comparison cannot tell
        them apart and would misclassify real data as more header.
        """
        return any(
            span.row_start <= row_index <= span.row_end and span.col_span > 1
            for span in table.cell_spans
        )

    def _path_for_column(
        self,
        *,
        table: TableAsset,
        column_index: int,
        header_row_count: int,
    ) -> tuple[str, ...]:
        segments: list[str] = []
        for row_index in range(header_row_count):
            candidate = self._span_text_for_cell(
                table=table,
                row_index=row_index,
                column_index=column_index,
            )
            if (
                not candidate
                and row_index < len(table.rows)
                and self._looks_uniform_umbrella_row(table.rows[row_index])
            ):
                candidate = self._uniform_row_label(table.rows[row_index])
            if (
                not candidate
                and row_index < len(table.rows)
                and column_index < len(table.rows[row_index])
            ):
                candidate = self.normalize_header_cell(table.rows[row_index][column_index])
            if not candidate:
                continue
            if segments and segments[-1] == candidate:
                continue
            segments.append(candidate)
        return tuple(segments)

    def _span_text_for_cell(
        self,
        *,
        table: TableAsset,
        row_index: int,
        column_index: int,
    ) -> str:
        for span in sorted(
            table.cell_spans,
            key=lambda item: (item.row_start, item.col_start, -item.col_span, -item.row_span),
        ):
            if not (
                span.row_start <= row_index <= span.row_end
                and span.col_start <= column_index <= span.col_end
            ):
                continue
            return self.normalize_header_cell(span.normalized_text or span.text)
        return ""

    def _looks_header_row(self, row: list[str]) -> bool:
        non_empty = [normalize_cell(cell) for cell in row if normalize_cell(cell)]
        if len(non_empty) < 2:
            return False
        numeric_like = sum(1 for cell in non_empty if looks_numeric(cell))
        if numeric_like >= max(1, len(non_empty) // 2):
            return False
        return any(
            looks_explicit_header_cell(cell) or looks_label_cell(cell)
            for cell in non_empty
        )

    def _looks_uniform_umbrella_row(self, row: list[str]) -> bool:
        non_empty = [normalize_cell(cell) for cell in row if normalize_cell(cell)]
        if not non_empty:
            return False
        if len(non_empty) == 1:
            return True
        normalized = {self.normalize_header_cell(cell) for cell in non_empty if cell}
        return len(normalized) == 1

    def _uniform_row_label(self, row: list[str]) -> str:
        for cell in row:
            cleaned = self.normalize_header_cell(cell)
            if cleaned:
                return cleaned
        return ""

    @staticmethod
    def collapse_uniform_umbrella(
        paths: tuple[tuple[str, ...], ...],
    ) -> tuple[tuple[str, ...], ...]:
        if len(paths) < 2:
            return paths
        first_segment = paths[0][0] if paths[0] else ""
        if not first_segment:
            return paths
        if not all(path and path[0] == first_segment for path in paths):
            return paths
        if not any(len(path) > 1 for path in paths):
            return paths
        collapsed: list[tuple[str, ...]] = []
        for path in paths:
            tail = path[1:]
            collapsed.append(tail or path)
        return tuple(collapsed)

    @staticmethod
    def normalize_header_cell(value: str | None) -> str:
        text = normalize_cell(value)
        if not text:
            return ""
        text = text.casefold()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s/%.-]", "", text)
        return text.strip()
