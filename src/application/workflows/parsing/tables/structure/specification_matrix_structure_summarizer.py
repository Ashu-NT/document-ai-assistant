from __future__ import annotations

from src.application.workflows.parsing.tables.structure.table_shape import (
    TableShape,
)
from src.application.workflows.parsing.tables.structure.table_structure_summary import (
    TableStructureSummary,
)
from src.domain.assets.table_rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.domain.assets.table_rows.table_row_patterns import (
    count_interval_columns,
    looks_explicit_header_cell,
    looks_interval_header,
    looks_label_cell,
    looks_numeric,
    normalize_cell,
)

_NOTES_HEADERS = {"note", "notes", "remark", "remarks"}
_TROUBLESHOOTING_HEADERS = {
    "action",
    "cause",
    "causes",
    "problem",
    "probable causes",
    "possible remedies",
    "remedies",
    "remedy",
    "symptom",
}
_UNIT_HEADERS = {"unit", "units"}
_IDENTITY_RECORD_HEADERS = {
    "manufacturer",
    "serial number",
    "location",
    "supplier",
}


class SpecificationMatrixStructureSummarizer:
    def __init__(
        self,
        *,
        row_canonicalizer: TableRowCanonicalizer | None = None,
    ) -> None:
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()

    def summarize(self, rows: list[list[str]]) -> TableStructureSummary | None:
        cleaned_rows = self.row_canonicalizer.canonicalize(rows)
        if not self._looks_like_specification_matrix(cleaned_rows):
            return None

        headers = [normalize_cell(cell) for cell in cleaned_rows[0]]
        axis_summary = {
            "row_axis": "parameter",
            "column_axis": "field",
            "value_axis": "specification_value",
        }
        if any(header.casefold() in _UNIT_HEADERS for header in headers[1:]):
            axis_summary["descriptor_axis"] = "unit"
        elif any(header.casefold() in _NOTES_HEADERS for header in headers[1:]):
            axis_summary["descriptor_axis"] = "notes"

        return TableStructureSummary(
            table_shape=TableShape.SPECIFICATION_MATRIX,
            quality_score=self._quality_score(cleaned_rows),
            header_paths=self._header_paths(headers),
            axis_summary=axis_summary,
        )

    def _looks_like_specification_matrix(self, rows: list[list[str]]) -> bool:
        if len(rows) < 2:
            return False

        headers = [normalize_cell(cell) for cell in rows[0]]
        non_empty_headers = [header for header in headers if header]
        if len(non_empty_headers) < 3:
            return False
        if count_interval_columns(headers) >= 2:
            return False
        if any(header.casefold() in _TROUBLESHOOTING_HEADERS for header in headers):
            return False
        if self._has_interval_header_signal(headers):
            return False
        if self._looks_like_identity_record_listing(headers):
            return False

        comparison_headers = [header for header in headers[1:] if header]
        if len(comparison_headers) < 2:
            return False
        numeric_header_count = sum(
            1 for header in comparison_headers if looks_numeric(header)
        )
        if numeric_header_count >= max(2, len(comparison_headers) // 2):
            return False
        if not (
            looks_explicit_header_cell(headers[0]) or looks_label_cell(headers[0])
        ):
            return False

        body_rows = rows[1:]
        first_column_labels = sum(
            1
            for row in body_rows
            if row and looks_label_cell(normalize_cell(row[0]))
        )
        if first_column_labels < max(1, len(body_rows) // 2):
            return False

        populated_comparison_columns: set[int] = set()
        non_empty_data_points = 0
        for row in body_rows:
            for index in range(1, min(len(row), len(headers))):
                cell = normalize_cell(row[index])
                if not cell:
                    continue
                populated_comparison_columns.add(index)
                non_empty_data_points += 1

        if len(populated_comparison_columns) < 2:
            return False
        if non_empty_data_points < max(2, len(body_rows)):
            return False

        header_signal_count = sum(
            1 for header in headers if looks_explicit_header_cell(header)
        )
        labeled_comparison_header_count = sum(
            1
            for header in comparison_headers
            if looks_label_cell(header) and not looks_numeric(header)
        )
        return header_signal_count >= 1 and (
            header_signal_count + labeled_comparison_header_count
        ) >= 2

    @staticmethod
    def _has_interval_header_signal(headers: list[str]) -> bool:
        """A table with a literal "Interval"-style column (free-text
        schedule descriptions like "Every 6 months", not just boolean
        schedule markers) belongs to the maintenance-schedule family, not
        a parameter/value comparison, regardless of what the first
        column is called ("Task", "Description", ...) - even though it
        can otherwise satisfy the generic label/header checks above.
        Left unclassified here rather than misrouted.
        """
        return any(
            "interval" in header.casefold() or looks_interval_header(header)
            for header in headers
        )

    @staticmethod
    def _looks_like_identity_record_listing(headers: list[str]) -> bool:
        """A listing of distinct real-world items identified by
        manufacturer/serial/location fields is a record table, not a
        specification comparison, even when each row has a label-like
        first cell and several populated text columns.
        """
        normalized = [header.casefold() for header in headers]
        identity_signal_count = sum(
            1 for header in normalized if header in _IDENTITY_RECORD_HEADERS
        )
        return identity_signal_count >= 2

    @staticmethod
    def _header_paths(headers: list[str]) -> list[list[str]]:
        paths: list[list[str]] = []
        for index, header in enumerate(headers):
            normalized = header.casefold()
            if index == 0:
                paths.append(["Parameter"])
            elif normalized in _UNIT_HEADERS:
                paths.append(["Unit"])
            elif normalized in _NOTES_HEADERS:
                paths.append(["Notes"])
            else:
                paths.append(["Field", header] if header else [])
        return paths

    @staticmethod
    def _quality_score(rows: list[list[str]]) -> float:
        headers = [normalize_cell(cell) for cell in rows[0]]
        body_rows = rows[1:]
        header_signal = sum(
            1 for header in headers if looks_explicit_header_cell(header)
        )
        first_column_labels = sum(
            1
            for row in body_rows
            if row and looks_label_cell(normalize_cell(row[0]))
        )
        comparison_width = max(1, len(headers) - 1)
        non_empty_data_points = sum(
            1
            for row in body_rows
            for index in range(1, min(len(row), len(headers)))
            if normalize_cell(row[index])
        )
        max_points = max(1, len(body_rows) * comparison_width)
        header_strength = min(1.0, header_signal / 3)
        label_strength = first_column_labels / max(1, len(body_rows))
        coverage = min(1.0, non_empty_data_points / max_points)
        score = 0.52 + (header_strength * 0.18) + (label_strength * 0.18) + (
            coverage * 0.12
        )
        return round(min(score, 0.98), 2)
