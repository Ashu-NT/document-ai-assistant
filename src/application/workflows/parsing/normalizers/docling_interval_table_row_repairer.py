from __future__ import annotations

import re


class DoclingIntervalTableRowRepairer:
    _DESCRIPTION_HEADERS = ("description", "task", "activity", "action")
    _INTERVAL_HEADERS = ("interval", "frequency", "schedule", "service interval")
    _INTERVAL_ANCHORS = (
        "first time",
        "after",
        "every",
        "when needed",
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "yearly",
        "annual",
        "annually",
        "operating hours",
        "running hours",
        "service life",
    )
    _WHITESPACE_PATTERN = re.compile(r"\s+")

    def repair(self, rows: list[list[str]]) -> list[list[str]]:
        if len(rows) < 2:
            return rows

        description_index = self._find_header_index(
            rows[0],
            self._DESCRIPTION_HEADERS,
        )
        interval_index = self._find_header_index(
            rows[0],
            self._INTERVAL_HEADERS,
        )
        if description_index is None or interval_index is None:
            return rows

        repaired = [list(row) for row in rows]
        for row in repaired[1:]:
            self._repair_row(
                row,
                description_index=description_index,
                interval_index=interval_index,
            )
        return repaired

    def _repair_row(
        self,
        row: list[str],
        *,
        description_index: int,
        interval_index: int,
    ) -> None:
        description = self._cell(row, description_index)
        interval = self._cell(row, interval_index)

        if not description and interval:
            split = self._split_leading_label(interval)
            if split is not None:
                row[description_index], row[interval_index] = split
                return

        if description and not interval:
            split = self._split_trailing_interval(description)
            if split is not None:
                row[description_index], row[interval_index] = split

    def _split_leading_label(self, value: str) -> tuple[str, str] | None:
        index = self._interval_anchor_index(value)
        if index is None:
            return None

        label = self._clean(value[:index])
        interval = self._clean(value[index:])
        if not label or not interval:
            return None
        if sum(character.isalpha() for character in label) < 3:
            return None
        return label, interval

    def _split_trailing_interval(self, value: str) -> tuple[str, str] | None:
        index = self._interval_anchor_index(value)
        if index is None:
            return None

        description = self._clean(value[:index])
        interval = self._clean(value[index:])
        if not description or not interval:
            return None
        if sum(character.isalpha() for character in description) < 3:
            return None
        return description, interval

    def _interval_anchor_index(self, value: str) -> int | None:
        normalized = self._clean(value).casefold()
        if not normalized:
            return None

        positions = [
            normalized.find(anchor)
            for anchor in self._INTERVAL_ANCHORS
            if normalized.find(anchor) > 0
        ]
        if not positions:
            return None
        return min(positions)

    @staticmethod
    def _find_header_index(headers: list[str], markers: tuple[str, ...]) -> int | None:
        for index, header in enumerate(headers):
            normalized = " ".join(str(header or "").split()).strip().casefold()
            if normalized and any(marker in normalized for marker in markers):
                return index
        return None

    @staticmethod
    def _cell(row: list[str], index: int) -> str:
        if index >= len(row):
            return ""
        return " ".join(str(row[index] or "").split()).strip()

    def _clean(self, value: str) -> str:
        return self._WHITESPACE_PATTERN.sub(" ", value).strip(" :-")
