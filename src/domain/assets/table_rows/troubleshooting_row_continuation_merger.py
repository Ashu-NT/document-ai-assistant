from __future__ import annotations

from src.application.workflows.parsing.tables.rows.row_continuation_patterns import (
    looks_like_continuation_pair,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    merge_continuation_text,
    normalize_cell,
)


class TroubleshootingRowContinuationMerger:
    def merge(
        self,
        *,
        headers: list[str],
        rows: list[list[str]],
    ) -> list[list[str]]:
        if len(rows) < 2:
            return rows

        indexes = self._indexes(headers)
        if indexes["symptom"] is None:
            return rows

        merged_rows: list[list[str]] = []
        for row in rows:
            normalized_row = [normalize_cell(cell) for cell in row]
            if not merged_rows:
                merged_rows.append(normalized_row)
                continue

            previous_row = merged_rows[-1]
            if not self._should_merge(previous_row, normalized_row, indexes=indexes):
                merged_rows.append(normalized_row)
                continue

            merged_rows[-1] = self._merge_rows(
                previous_row,
                normalized_row,
                indexes=indexes,
            )
        return merged_rows

    @staticmethod
    def _indexes(headers: list[str]) -> dict[str, int | None]:
        header_map = {
            normalize_cell(header).casefold(): index
            for index, header in enumerate(headers)
            if normalize_cell(header)
        }
        return {
            "symptom": header_map.get("symptom"),
            "cause": header_map.get("cause"),
            "remedy": header_map.get("remedy"),
            "notes": header_map.get("notes"),
        }

    def _should_merge(
        self,
        previous_row: list[str],
        current_row: list[str],
        *,
        indexes: dict[str, int | None],
    ) -> bool:
        if not self._same_or_missing(
            self._field(previous_row, indexes["symptom"]),
            self._field(current_row, indexes["symptom"]),
        ):
            return False

        return (
            self._should_merge_field(
                previous_row,
                current_row,
                field_name="cause",
                companion_name="remedy",
                indexes=indexes,
            )
            or self._should_merge_field(
                previous_row,
                current_row,
                field_name="remedy",
                companion_name="cause",
                indexes=indexes,
            )
        )

    def _should_merge_field(
        self,
        previous_row: list[str],
        current_row: list[str],
        *,
        field_name: str,
        companion_name: str,
        indexes: dict[str, int | None],
    ) -> bool:
        previous_value = self._field(previous_row, indexes[field_name])
        current_value = self._field(current_row, indexes[field_name])
        companion_previous = self._field(previous_row, indexes[companion_name])
        companion_current = self._field(current_row, indexes[companion_name])
        if not self._same_or_missing(companion_previous, companion_current):
            return False
        return self._looks_split_fragment(previous_value, current_value)

    def _merge_rows(
        self,
        previous_row: list[str],
        current_row: list[str],
        *,
        indexes: dict[str, int | None],
    ) -> list[str]:
        merged_row = list(previous_row)
        for field_name in ("symptom", "cause", "remedy", "notes"):
            index = indexes[field_name]
            if index is None:
                continue
            previous_value = self._field(previous_row, index)
            current_value = self._field(current_row, index)
            merged_row[index] = self._merge_text(previous_value, current_value)
        return merged_row

    def _looks_split_fragment(self, previous_value: str, current_value: str) -> bool:
        return looks_like_continuation_pair(previous_value, current_value)

    @staticmethod
    def _same_or_missing(left: str, right: str) -> bool:
        if not left or not right:
            return True
        return left.casefold() == right.casefold()

    @staticmethod
    def _field(row: list[str], index: int | None) -> str:
        if index is None or index >= len(row):
            return ""
        return normalize_cell(row[index])

    @staticmethod
    def _merge_text(previous_value: str, current_value: str) -> str:
        return merge_continuation_text(previous_value, current_value)
