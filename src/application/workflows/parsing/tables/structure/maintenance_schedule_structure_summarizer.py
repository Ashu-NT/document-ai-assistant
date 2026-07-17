from __future__ import annotations

from src.application.workflows.parsing.tables.semantics.table_matrix_detector import (
    TableMatrixDetector,
)
from src.application.workflows.parsing.tables.structure.table_structure_summary import (
    TableStructureSummary,
)
from src.application.workflows.shared.table_shape import TableShape
from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    count_boolean_markers,
    count_interval_columns,
    looks_interval_header,
    normalize_cell,
)


class MaintenanceScheduleStructureSummarizer:
    def __init__(
        self,
        *,
        matrix_detector: TableMatrixDetector | None = None,
        row_canonicalizer: TableRowCanonicalizer | None = None,
    ) -> None:
        self.matrix_detector = matrix_detector or TableMatrixDetector()
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()

    def summarize(self, rows: list[list[str]]) -> TableStructureSummary | None:
        cleaned_rows = self.row_canonicalizer.canonicalize(rows)
        if not self.matrix_detector.is_maintenance_interval_matrix(cleaned_rows):
            return None
        if len(cleaned_rows) < 2:
            return None

        headers = [normalize_cell(cell) for cell in cleaned_rows[0]]
        interval_indexes = {
            index for index, header in enumerate(headers) if looks_interval_header(header)
        }
        task_index = self._task_index(headers, interval_indexes)
        notes_index = self._notes_index(headers, interval_indexes, task_index)
        header_paths = self._header_paths(
            headers=headers,
            interval_indexes=interval_indexes,
            task_index=task_index,
            notes_index=notes_index,
        )
        quality_score = self._quality_score(
            headers=headers,
            rows=cleaned_rows[1:],
            interval_indexes=interval_indexes,
        )
        axis_summary = {
            "row_axis": "task",
            "column_axis": "interval",
            "value_axis": "marker",
        }
        if notes_index is not None:
            axis_summary["descriptor_axis"] = "notes"

        return TableStructureSummary(
            table_shape=TableShape.MAINTENANCE_SCHEDULE_MATRIX,
            quality_score=quality_score,
            header_paths=header_paths,
            axis_summary=axis_summary,
        )

    @staticmethod
    def _task_index(
        headers: list[str],
        interval_indexes: set[int],
    ) -> int | None:
        candidates = [
            index
            for index, header in enumerate(headers)
            if index not in interval_indexes and header
        ]
        return candidates[0] if candidates else None

    @staticmethod
    def _notes_index(
        headers: list[str],
        interval_indexes: set[int],
        task_index: int | None,
    ) -> int | None:
        for index, header in enumerate(headers):
            if index in interval_indexes or index == task_index:
                continue
            normalized = header.casefold()
            if normalized in {"note", "notes", "reference", "task reference"}:
                return index
        return None

    def _header_paths(
        self,
        *,
        headers: list[str],
        interval_indexes: set[int],
        task_index: int | None,
        notes_index: int | None,
    ) -> list[list[str]]:
        paths: list[list[str]] = []
        for index, header in enumerate(headers):
            if index in interval_indexes:
                paths.append(["Interval", header])
                continue
            if index == task_index:
                paths.append(["Task"])
                continue
            if index == notes_index:
                paths.append(["Notes"])
                continue
            paths.append([header] if header else [])
        return paths

    @staticmethod
    def _quality_score(
        *,
        headers: list[str],
        rows: list[list[str]],
        interval_indexes: set[int],
    ) -> float:
        positives, inspected = count_boolean_markers(
            rows,
            column_indexes=interval_indexes,
        )
        interval_strength = min(1.0, count_interval_columns(headers) / 4)
        marker_strength = positives / inspected if inspected else 0.0
        score = 0.55 + (interval_strength * 0.2) + (marker_strength * 0.25)
        return round(min(score, 0.98), 2)
