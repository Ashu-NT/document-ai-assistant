from __future__ import annotations

from src.domain.assets.table_rows.table_row_patterns import normalize_cell

_OPEN_ENDINGS = (
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
    "without",
)
_TERMINAL_PUNCTUATION = (".", "!", "?", ";", ":")


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
        if not previous_value or not current_value:
            return False
        if previous_value.casefold() == current_value.casefold():
            return False
        if self._looks_incomplete(previous_value):
            return True
        return (
            not self._looks_terminated(previous_value)
            and self._looks_continuation_start(current_value)
        )

    @staticmethod
    def _looks_incomplete(value: str) -> bool:
        if not value or TroubleshootingRowContinuationMerger._looks_terminated(value):
            return False
        tokens = value.casefold().split()
        if not tokens:
            return False
        return tokens[-1] in _OPEN_ENDINGS or value.endswith(("-", "/", ","))

    @staticmethod
    def _looks_terminated(value: str) -> bool:
        return value.rstrip().endswith(_TERMINAL_PUNCTUATION)

    @staticmethod
    def _looks_continuation_start(value: str) -> bool:
        stripped = value.lstrip()
        return bool(stripped) and stripped[0].islower()

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
        if not previous_value:
            return current_value
        if not current_value or previous_value.casefold() == current_value.casefold():
            return previous_value
        if previous_value.endswith("-"):
            return f"{previous_value[:-1]}{current_value}".strip()
        return f"{previous_value} {current_value}".strip()
