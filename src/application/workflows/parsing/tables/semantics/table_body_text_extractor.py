from __future__ import annotations

from src.application.workflows.parsing.tables.semantics.table_text_signal_matcher import (
    TableTextSignalMatcher,
)


class TableBodyTextExtractor:
    def __init__(self, *, signal_matcher: TableTextSignalMatcher | None = None) -> None:
        self.signal_matcher = signal_matcher or TableTextSignalMatcher()

    def body_label_cells(
        self,
        rows: list[list[str]],
        *,
        has_header_row: bool,
    ) -> list[str]:
        labels: list[str] = []
        for row in rows:
            non_empty = [str(cell or "").strip().casefold() for cell in row if str(cell or "").strip()]
            if len(non_empty) >= 2:
                labels.append(non_empty[0])
            elif not has_header_row and non_empty:
                labels.append(non_empty[0])
        return labels

    def body_text(self, rows: list[list[str]]) -> str:
        return self.signal_matcher.normalized_text(
            *[
                str(cell or "").strip()
                for row in rows
                for cell in row
                if str(cell or "").strip()
            ]
        )
