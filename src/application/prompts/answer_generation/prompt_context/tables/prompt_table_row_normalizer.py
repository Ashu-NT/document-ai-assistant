from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models.prompt_table_row_view import (
    PromptTableRowView,
)


class PromptTableRowNormalizer:
    def normalize(
        self,
        rows: list[list[str]],
    ) -> tuple[list[str], list[PromptTableRowView]]:
        cleaned_rows = [self._clean_row(row) for row in rows if self._clean_row(row)]
        if not cleaned_rows:
            return [], []
        has_headers = self._has_header_row(cleaned_rows)
        headers = cleaned_rows[0] if has_headers else []
        start_index = 1 if has_headers else 0
        normalized_rows = [
            PromptTableRowView(
                source_row_index=row_index,
                cells=list(row),
                cells_by_header=self._cells_by_header(headers, row),
            )
            for row_index, row in enumerate(cleaned_rows[start_index:], start=start_index)
        ]
        return headers, normalized_rows

    @staticmethod
    def _clean_row(row: list[str]) -> list[str]:
        cleaned = [" ".join(str(cell).split()).strip() for cell in row]
        return [cell for cell in cleaned if cell]

    def _has_header_row(self, rows: list[list[str]]) -> bool:
        if len(rows) < 2:
            return False
        header = rows[0]
        if len(header) < 2:
            return False
        normalized_header = [cell.lower() for cell in header if cell]
        if len(normalized_header) != len(header):
            return False
        if len(set(normalized_header)) != len(normalized_header):
            return False
        numeric_like = sum(1 for cell in header if self._looks_numeric(cell))
        return numeric_like < max(1, len(header) // 2)

    @staticmethod
    def _cells_by_header(headers: list[str], row: list[str]) -> dict[str, str]:
        if not headers:
            return {}
        return {
            header: row[index]
            for index, header in enumerate(headers)
            if header and index < len(row) and row[index]
        }

    @staticmethod
    def _looks_numeric(value: str) -> bool:
        stripped = value.strip().replace(",", "").replace(".", "").replace("-", "")
        return bool(stripped) and stripped.isdigit()
