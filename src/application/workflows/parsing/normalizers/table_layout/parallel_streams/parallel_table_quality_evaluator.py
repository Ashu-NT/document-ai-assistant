from __future__ import annotations


class ParallelTableQualityEvaluator:
    def density(self, rows: list[list[str]]) -> float:
        if not rows:
            return 0.0
        width = max((len(row) for row in rows), default=0)
        if width <= 0:
            return 0.0
        total_cells = len(rows) * width
        non_empty = sum(
            1
            for row in rows
            for cell in row
            if str(cell).strip()
        )
        return non_empty / total_cells if total_cells else 0.0

    def score(self, rows: list[list[str]]) -> float:
        if not rows:
            return 0.0
        density = self.density(rows)
        width = max((len(row) for row in rows), default=0)
        header_bonus = self._header_bonus(rows[0])
        data_row_bonus = min(0.2, 0.04 * max(0, len(rows) - 1))
        width_bonus = 0.08 if width >= 2 else 0.0
        return (density * 0.6) + header_bonus + data_row_bonus + width_bonus

    @staticmethod
    def _header_bonus(row: list[str]) -> float:
        non_empty = [str(cell).strip() for cell in row if str(cell).strip()]
        if len(non_empty) < 2:
            return 0.0
        alpha_cells = sum(
            1
            for cell in non_empty
            if any(character.isalpha() for character in cell)
        )
        if alpha_cells < max(1, len(non_empty) // 2):
            return 0.0
        return min(0.22, 0.05 * len(non_empty))
