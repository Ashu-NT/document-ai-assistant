from __future__ import annotations

from src.domain.assets.table_rows.table_row_patterns import normalize_cell

_OPEN_ENDINGS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "been",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
    "without",
}
_TERMINAL_PUNCTUATION = (".", "!", "?", ";", ":")
_CONTINUATION_PREFIXES = ("(", "-", "*", "/", "•", "·")


class DoclingSparseContinuationRowMerger:
    """Attaches sparse subordinate rows to the most recent compatible row."""

    def merge(self, rows: list[list[str]]) -> list[list[str]]:
        if len(rows) < 2:
            return rows

        merged_rows: list[list[str]] = []
        for row in rows:
            normalized_row = [normalize_cell(cell) for cell in row]
            if not merged_rows:
                merged_rows.append(normalized_row)
                continue

            previous_row = merged_rows[-1]
            if not self._should_attach(previous_row, normalized_row):
                merged_rows.append(normalized_row)
                continue

            merged_rows[-1] = self._attach(previous_row, normalized_row)
        return merged_rows

    def _should_attach(self, previous_row: list[str], current_row: list[str]) -> bool:
        current_indexes = self._non_empty_indexes(current_row)
        if not current_indexes or current_indexes[0] == 0:
            return False
        if any(
            index >= len(previous_row) or not normalize_cell(previous_row[index])
            for index in current_indexes
        ):
            return False
        return any(
            self._looks_like_continuation(previous_row[index], current_row[index])
            for index in current_indexes
        )

    @staticmethod
    def _non_empty_indexes(row: list[str]) -> list[int]:
        return [index for index, value in enumerate(row) if normalize_cell(value)]

    def _looks_like_continuation(self, previous_value: str, current_value: str) -> bool:
        previous = normalize_cell(previous_value)
        current = normalize_cell(current_value)
        if not previous or not current:
            return False
        if previous.casefold() == current.casefold():
            return False
        if previous.endswith("-"):
            return True
        if self._looks_incomplete(previous):
            return True
        return not self._looks_terminated(previous) and self._looks_continuation_start(
            current
        )

    @staticmethod
    def _looks_incomplete(value: str) -> bool:
        if not value or DoclingSparseContinuationRowMerger._looks_terminated(value):
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
        if not stripped:
            return False
        if stripped[0].islower() or stripped[0].isdigit():
            return True
        return stripped.startswith(_CONTINUATION_PREFIXES)

    def _attach(self, previous_row: list[str], current_row: list[str]) -> list[str]:
        merged = list(previous_row)
        for index, value in enumerate(current_row):
            normalized = normalize_cell(value)
            if not normalized:
                continue
            merged[index] = self._merge_text(merged[index], normalized)
        return merged

    @staticmethod
    def _merge_text(previous_value: str, current_value: str) -> str:
        previous = normalize_cell(previous_value)
        current = normalize_cell(current_value)
        if not previous:
            return current
        if not current or previous.casefold() == current.casefold():
            return previous
        if previous.endswith("-"):
            return f"{previous[:-1]}{current}".strip()
        return f"{previous} {current}".strip()
