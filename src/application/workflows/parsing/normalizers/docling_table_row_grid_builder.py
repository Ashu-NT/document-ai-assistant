from __future__ import annotations

import re
from typing import Any

from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.application.workflows.parsing.normalizers.docling_table_row_repairer import (
    DoclingTableRowRepairer,
)
from src.application.workflows.parsing.tables.structure.compact_interval_header_token_matcher import (
    CompactIntervalHeaderTokenMatcher,
)
from src.config.settings import docling_settings
from src.shared.exceptions import DocumentNormalizationError


class DoclingTableRowGridBuilder:
    """Builds a best-effort row grid from Docling table cell spans."""

    def __init__(
        self,
        *,
        row_repairer: DoclingTableRowRepairer | None = None,
        interval_header_matcher: CompactIntervalHeaderTokenMatcher | None = None,
    ) -> None:
        self.row_repairer = row_repairer or DoclingTableRowRepairer()
        self.interval_header_matcher = (
            interval_header_matcher or CompactIntervalHeaderTokenMatcher()
        )

    def build_rows(self, table_cells: list[Any]) -> list[list[str]]:
        spans = [
            _Span.from_raw(cell)
            for cell in table_cells
        ]
        spans = [span for span in spans if span is not None]
        if not spans:
            return []

        max_row = max(span.row_end for span in spans)
        max_col = max(span.col_end for span in spans)
        self._guard_grid_size(max_row=max_row, max_col=max_col)
        grid = [
            ["" for _ in range(max_col + 1)]
            for _ in range(max_row + 1)
        ]

        for span in sorted(
            spans,
            key=lambda item: (
                item.row_start,
                item.col_start,
                item.row_span,
                item.col_span,
            ),
        ):
            if self._distribute_interval_header_tokens(grid, span):
                continue
            self._write_span(grid, span)

        rows = [
            row
            for row in grid
            if any(cell.strip() for cell in row)
        ]
        return self.row_repairer.repair_rows(rows)

    @staticmethod
    def _guard_grid_size(*, max_row: int, max_col: int) -> None:
        """A single malformed cell span with a corrupted, very large
        offset would otherwise cause an unbounded, slow grid allocation
        (multi-GB scale) with no signal - fail loudly instead so a bad
        document surfaces as a clear parsing error, not a hang.
        """
        cell_count = (max_row + 1) * (max_col + 1)
        if cell_count > docling_settings.max_table_grid_cells:
            raise DocumentNormalizationError(
                "Docling table cell spans imply an implausibly large grid.",
                details={
                    "max_row": max_row,
                    "max_col": max_col,
                    "cell_count": cell_count,
                    "max_table_grid_cells": docling_settings.max_table_grid_cells,
                },
            )

    def _distribute_interval_header_tokens(
        self,
        grid: list[list[str]],
        span: "_Span",
    ) -> bool:
        if span.row_start != 0 or span.row_span != 1 or span.col_span <= 1:
            return False

        tokens = [
            token
            for token in re.split(r"[\s/|,;]+", span.text)
            if token
        ]
        if len(tokens) != span.col_span:
            return False
        if not all(self.interval_header_matcher.matches(token) for token in tokens):
            return False

        for offset, token in enumerate(tokens):
            grid[span.row_start][span.col_start + offset] = token
        return True

    def _write_span(
        self,
        grid: list[list[str]],
        span: "_Span",
    ) -> None:
        self._merge_cell(
            grid,
            row_index=span.row_start,
            column_index=span.col_start,
            text=span.text,
        )

        if span.row_span > 1 and span.col_span == 1:
            for row_index in range(span.row_start + 1, span.row_end + 1):
                self._merge_cell(
                    grid,
                    row_index=row_index,
                    column_index=span.col_start,
                    text=span.text,
                )

    @staticmethod
    def _merge_cell(
        grid: list[list[str]],
        *,
        row_index: int,
        column_index: int,
        text: str,
    ) -> None:
        existing = grid[row_index][column_index].strip()
        if not existing:
            grid[row_index][column_index] = text
            return
        if existing == text:
            return
        grid[row_index][column_index] = f"{existing} {text}".strip()


class _Span:
    def __init__(
        self,
        *,
        row_start: int,
        row_end: int,
        col_start: int,
        col_end: int,
        text: str,
    ) -> None:
        self.row_start = row_start
        self.row_end = row_end
        self.col_start = col_start
        self.col_end = col_end
        self.text = text

    @property
    def row_span(self) -> int:
        return max(1, self.row_end - self.row_start + 1)

    @property
    def col_span(self) -> int:
        return max(1, self.col_end - self.col_start + 1)

    @classmethod
    def from_raw(cls, value: Any) -> "_Span | None":
        row_start = _coerce_int(_get_value(value, "start_row_offset_idx"))
        row_end = _coerce_int(_get_value(value, "end_row_offset_idx"))
        col_start = _coerce_int(_get_value(value, "start_col_offset_idx"))
        col_end = _coerce_int(_get_value(value, "end_col_offset_idx"))
        text = _clean_text(_get_value(value, "text"))
        if (
            row_start is None
            or col_start is None
            or not text
        ):
            return None

        resolved_row_end = max(row_start, (row_end - 1) if row_end is not None else row_start)
        resolved_col_end = max(col_start, (col_end - 1) if col_end is not None else col_start)
        return cls(
            row_start=row_start,
            row_end=resolved_row_end,
            col_start=col_start,
            col_end=resolved_col_end,
            text=text,
        )


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(repair_docling_text(str(value)).split()).strip()
    return text or None


def _get_value(value: Any, name: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None)
