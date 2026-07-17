from __future__ import annotations

from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)

_MIN_SHARED_ROWS = 2
_MIN_MATCH_RATIO = 0.75
_MIN_SUBSTANTIVE_MATCHES = 2


class DoclingTemplateDuplicateColumnCollapser:
    """Collapses adjacent columns that carry duplicated template payload."""

    def collapse(self, rows: list[list[str]]) -> list[list[str]]:
        if len(rows) < 2:
            return rows

        width = max((len(row) for row in rows), default=0)
        if width < 3:
            return rows

        duplicate_groups = self._build_groups(rows, width=width)
        if not duplicate_groups:
            return rows

        return [
            self._collapse_row(row, groups=duplicate_groups, width=width)
            for row in rows
        ]

    def _build_groups(
        self,
        rows: list[list[str]],
        *,
        width: int,
    ) -> tuple[tuple[int, ...], ...]:
        groups: list[tuple[int, ...]] = []
        index = 0
        while index < width - 1:
            group = [index]
            candidate = index + 1
            while candidate < width and self._columns_are_duplicates(
                rows,
                group[0],
                candidate,
            ):
                group.append(candidate)
                candidate += 1
            if len(group) > 1:
                groups.append(tuple(group))
                index = group[-1] + 1
                continue
            index += 1
        return tuple(groups)

    def _columns_are_duplicates(
        self,
        rows: list[list[str]],
        left_index: int,
        right_index: int,
    ) -> bool:
        shared_rows = 0
        matched_rows = 0
        substantive_matches = 0
        mismatched_rows = 0

        for row in rows:
            left = self._value_at(row, left_index)
            right = self._value_at(row, right_index)
            if not left or not right:
                continue

            shared_rows += 1
            if self._cells_equivalent(left, right):
                matched_rows += 1
                if self._looks_substantive(left) or self._looks_substantive(right):
                    substantive_matches += 1
                continue

            mismatched_rows += 1

        if shared_rows < _MIN_SHARED_ROWS:
            return False
        if substantive_matches < _MIN_SUBSTANTIVE_MATCHES:
            return False
        if matched_rows / shared_rows < _MIN_MATCH_RATIO:
            return False
        return mismatched_rows <= max(1, shared_rows // 4)

    @staticmethod
    def _value_at(row: list[str], index: int) -> str:
        if index >= len(row):
            return ""
        return normalize_cell(row[index])

    def _collapse_row(
        self,
        row: list[str],
        *,
        groups: tuple[tuple[int, ...], ...],
        width: int,
    ) -> list[str]:
        group_starts = {group[0]: group for group in groups}
        suppressed_indexes = {
            index
            for group in groups
            for index in group[1:]
        }

        collapsed: list[str] = []
        for index in range(width):
            if index in suppressed_indexes:
                continue
            if index not in group_starts:
                collapsed.append(self._value_at(row, index))
                continue

            group_values = [self._value_at(row, column_index) for column_index in group_starts[index]]
            collapsed.append(self._richest_value(group_values))
        return collapsed

    @staticmethod
    def _cells_equivalent(left: str, right: str) -> bool:
        left_norm = normalize_cell(left).casefold()
        right_norm = normalize_cell(right).casefold()
        if left_norm == right_norm:
            return True
        if len(left_norm) >= 8 and len(right_norm) >= 8:
            if left_norm in right_norm or right_norm in left_norm:
                return True

        left_tokens = {token for token in left_norm.split() if token}
        right_tokens = {token for token in right_norm.split() if token}
        if not left_tokens or not right_tokens:
            return False

        overlap = left_tokens & right_tokens
        if len(overlap) < 2:
            return False
        return len(overlap) / min(len(left_tokens), len(right_tokens)) >= 0.8

    @staticmethod
    def _looks_substantive(value: str) -> bool:
        normalized = normalize_cell(value)
        return sum(character.isalpha() for character in normalized) >= 4

    @staticmethod
    def _richest_value(values: list[str]) -> str:
        candidates = [normalize_cell(value) for value in values if normalize_cell(value)]
        if not candidates:
            return ""
        return max(
            candidates,
            key=lambda value: (
                sum(character.isalpha() for character in value),
                len(value.split()),
                len(value),
            ),
        )
