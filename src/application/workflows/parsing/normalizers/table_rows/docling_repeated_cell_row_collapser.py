from __future__ import annotations


class DoclingRepeatedCellRowCollapser:
    """Collapses merged-label rows that Docling repeats across many columns."""

    def collapse(self, rows: list[list[str]]) -> list[list[str]]:
        collapsed_rows: list[list[str]] = []
        for row in rows:
            collapsed_rows.append(self._collapse_row(row))
        return collapsed_rows

    def _collapse_row(self, row: list[str]) -> list[str]:
        normalized_cells = [self._normalize(cell) for cell in row]
        non_empty_cells = [cell for cell in normalized_cells if cell]
        if len(non_empty_cells) < 3:
            return row
        if len(set(non_empty_cells)) != 1:
            return row

        repeated_value = non_empty_cells[0]
        if self._looks_marker_like(repeated_value):
            return row

        return [repeated_value, *([""] * (len(row) - 1))]

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(str(value or "").split()).strip()

    @classmethod
    def _looks_marker_like(cls, value: str) -> bool:
        normalized = cls._normalize(value).casefold()
        if not normalized:
            return True
        if normalized in {"1", "check", "required", "x", "yes", "y"}:
            return True
        return sum(character.isalpha() for character in normalized) < 2
