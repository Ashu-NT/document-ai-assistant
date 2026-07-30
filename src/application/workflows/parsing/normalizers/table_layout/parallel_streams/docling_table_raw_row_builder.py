from __future__ import annotations

import re

from src.application.workflows.parsing.tables.structure.compact_interval_header_token_matcher import (
    CompactIntervalHeaderTokenMatcher,
)
from src.config.settings import docling_settings
from src.domain.assets import TableCellSpan
from src.shared.exceptions import DocumentNormalizationError


class DoclingTableRawRowBuilder:
    def __init__(
        self,
        *,
        interval_header_matcher: CompactIntervalHeaderTokenMatcher | None = None,
    ) -> None:
        self.interval_header_matcher = (
            interval_header_matcher or CompactIntervalHeaderTokenMatcher()
        )

    def build_rows(self, spans: list[TableCellSpan]) -> list[list[str]]:
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

        return [
            row
            for row in grid
            if any(cell.strip() for cell in row)
        ]

    @staticmethod
    def _guard_grid_size(*, max_row: int, max_col: int) -> None:
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
        span: TableCellSpan,
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
        span: TableCellSpan,
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
