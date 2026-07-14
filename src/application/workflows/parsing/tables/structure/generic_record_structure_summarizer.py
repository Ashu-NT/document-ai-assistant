from __future__ import annotations

from src.application.workflows.parsing.tables.structure.table_header_path_builder import (
    TableHeaderPathBuilder,
)
from src.application.workflows.parsing.tables.structure.table_shape import (
    TableShape,
)
from src.application.workflows.parsing.tables.structure.table_structure_summary import (
    TableStructureSummary,
)
from src.domain.assets import TableAsset
from src.domain.assets.table_rows.table_row_patterns import normalize_cell


class GenericRecordStructureSummarizer:
    def __init__(
        self,
        *,
        header_path_builder: TableHeaderPathBuilder | None = None,
    ) -> None:
        self.header_path_builder = header_path_builder or TableHeaderPathBuilder()

    def summarize(self, table: TableAsset) -> TableStructureSummary | None:
        if len(table.rows) < 2:
            return None

        header_row_count = self.header_path_builder.resolve_header_row_count(table)
        if len(table.rows) <= header_row_count:
            return None

        header_paths = [
            list(path)
            for path in self.header_path_builder.build_umbrella_collapsed_paths(table)
        ]
        if len(header_paths) < 2:
            return None

        if not self._has_signal_headers(header_paths):
            return None

        quality_score = self._quality_score(
            table=table,
            header_paths=header_paths,
            header_row_count=header_row_count,
        )
        return TableStructureSummary(
            table_shape=TableShape.RECORD_TABLE,
            quality_score=quality_score,
            header_paths=header_paths,
            axis_summary={
                "row_axis": "record",
                "column_axis": "attribute",
                "value_axis": "cell_value",
            },
        )

    @staticmethod
    def _has_signal_headers(header_paths: list[list[str]]) -> bool:
        meaningful_paths = [path for path in header_paths if any(part.strip() for part in path)]
        if len(meaningful_paths) < 2:
            return False
        non_numeric_term_count = 0
        for path in meaningful_paths:
            tail = path[-1]
            if any(character.isalpha() for character in tail):
                non_numeric_term_count += 1
        return non_numeric_term_count >= 2

    @staticmethod
    def _quality_score(
        *,
        table: TableAsset,
        header_paths: list[list[str]],
        header_row_count: int,
    ) -> float:
        data_rows = max(0, len(table.rows) - header_row_count)
        populated_headers = sum(1 for path in header_paths if any(path))
        rich_headers = sum(1 for path in header_paths if len(path) > 1)
        score = 0.55
        if populated_headers >= 3:
            score += 0.10
        if data_rows >= 2:
            score += 0.10
        if rich_headers >= 1:
            score += 0.10
        first_data_row = table.rows[header_row_count] if header_row_count < len(table.rows) else []
        if any(normalize_cell(cell) for cell in first_data_row):
            score += 0.05
        return min(score, 0.90)
