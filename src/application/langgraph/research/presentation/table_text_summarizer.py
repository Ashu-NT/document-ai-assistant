from __future__ import annotations

import re


class TableTextSummarizer:
    _SPEC_PREFERRED_KEYS = (
        "press type",
        "serial number",
        "drive type",
        "drive specification",
        "voltage",
        "installed power",
        "tank capacity",
        "pump capacity",
        "flow rate",
        "speed",
        "weight",
        "material",
        "max dp",
        "pressure",
        "year of manufacture",
        "specification",
    )
    _MAINTENANCE_PREFERRED_KEYS = (
        "maintenance interval",
        "interval",
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "annual",
        "half-yearly",
        "operating hours",
        "oil change",
        "inspection",
        "lubrication",
        "shutdown",
        "isolation",
    )

    def extract_pairs(self, text: str) -> list[tuple[str, str]]:
        rows = self._parse_table_rows(text)
        if not rows:
            return []
        pairs = self._rows_to_pairs(rows)
        normalized_pairs: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for label, value in pairs:
            cleaned_label = self._clean_cell(label)
            cleaned_value = self._clean_cell(value)
            if not cleaned_label or not cleaned_value:
                continue
            key = (
                self._normalize_key(cleaned_label),
                self._normalize_key(cleaned_value),
            )
            if key in seen:
                continue
            seen.add(key)
            normalized_pairs.append((cleaned_label, cleaned_value))
        return normalized_pairs

    def summarize(
        self,
        text: str,
        *,
        topic_hint: str | None = None,
        max_pairs: int = 6,
    ) -> list[str]:
        pairs = self.extract_pairs(text)
        if not pairs:
            return []
        ranked = self._rank_pairs(pairs, topic_hint=topic_hint)
        return [f"{label}: {value}" for label, value in ranked[:max_pairs]]

    def _rank_pairs(
        self,
        pairs: list[tuple[str, str]],
        *,
        topic_hint: str | None,
    ) -> list[tuple[str, str]]:
        normalized_hint = self._normalize_key(topic_hint or "")
        if self._looks_like_specification_topic(normalized_hint):
            preferred = self._SPEC_PREFERRED_KEYS
        elif self._looks_like_maintenance_topic(normalized_hint):
            preferred = self._MAINTENANCE_PREFERRED_KEYS
        else:
            preferred = self._SPEC_PREFERRED_KEYS + self._MAINTENANCE_PREFERRED_KEYS

        scored: list[tuple[int, int, tuple[str, str]]] = []
        for index, pair in enumerate(pairs):
            label, value = pair
            normalized_label = self._normalize_key(label)
            normalized_value = self._normalize_key(value)
            score = 0
            for rank, marker in enumerate(preferred):
                if marker in normalized_label:
                    score += 100 - rank
            if normalized_hint:
                for token in normalized_hint.split():
                    if token and token in normalized_label:
                        score += 8
                    if token and token in normalized_value:
                        score += 3
            if self._looks_like_identifier_label(normalized_label):
                score += 12
            if self._looks_like_unit_value(normalized_value):
                score += 6
            scored.append((score, -index, pair))
        scored.sort(reverse=True)
        return [pair for _, _, pair in scored]

    def _rows_to_pairs(self, rows: list[list[str]]) -> list[tuple[str, str]]:
        if len(rows) == 1 and len(rows[0]) >= 2 and len(rows[0]) % 2 == 0:
            row = rows[0]
            return [
                (row[index], row[index + 1])
                for index in range(0, len(row) - 1, 2)
            ]
        if len(rows) == 2 and len(rows[0]) == len(rows[1]) and len(rows[0]) > 1:
            return [
                (header, value)
                for header, value in zip(rows[0], rows[1], strict=False)
                if header and value
            ]

        pairs: list[tuple[str, str]] = []
        header = rows[0]
        if len(header) == 2:
            for row in rows[1:]:
                if len(row) >= 2:
                    pairs.append((row[0], row[1]))
            return pairs

        for row in rows:
            if len(row) >= 2 and len(row) % 2 == 0:
                for index in range(0, len(row) - 1, 2):
                    pairs.append((row[index], row[index + 1]))
        return pairs

    def _parse_table_rows(self, text: str) -> list[list[str]]:
        rows: list[list[str]] = []
        for line in text.splitlines():
            if "|" not in line:
                continue
            cells = [self._clean_cell(cell) for cell in line.split("|")]
            cells = [cell for cell in cells if cell]
            if len(cells) < 2:
                continue
            if all(re.fullmatch(r"[:\-]+", cell) for cell in cells):
                continue
            rows.append(cells)
        return rows

    @staticmethod
    def _looks_like_identifier_label(value: str) -> bool:
        return any(
            marker in value
            for marker in ("type", "serial", "model", "code", "number", "specification")
        )

    @staticmethod
    def _looks_like_unit_value(value: str) -> bool:
        return any(
            marker in value
            for marker in (" v", " hz", " kw", " kg", " l", " bar", " rpm", "m3", "hr")
        )

    @staticmethod
    def _looks_like_specification_topic(value: str) -> bool:
        return any(
            marker in value
            for marker in (
                "specification",
                "technical",
                "data",
                "pump",
                "capacity",
                "voltage",
                "ordering",
            )
        )

    @staticmethod
    def _looks_like_maintenance_topic(value: str) -> bool:
        return any(
            marker in value
            for marker in (
                "maintenance",
                "interval",
                "procedure",
                "inspection",
                "lubrication",
                "safety",
                "shutdown",
            )
        )

    @staticmethod
    def _clean_cell(value: str) -> str:
        return " ".join(value.strip().split())

    @staticmethod
    def _normalize_key(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()
