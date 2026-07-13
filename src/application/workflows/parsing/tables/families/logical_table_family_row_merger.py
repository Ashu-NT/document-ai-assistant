from __future__ import annotations

from typing import Sequence

from src.domain.assets import TableAsset


class LogicalTableFamilyRowMerger:
    def merge_tables(self, tables: Sequence[TableAsset]) -> list[list[str]] | None:
        row_groups = [table.rows for table in tables if table.rows]
        return self.merge_row_groups(row_groups)

    def merge_row_groups(
        self,
        row_groups: Sequence[Sequence[Sequence[str]]],
    ) -> list[list[str]] | None:
        merged_rows: list[list[str]] = []
        merged_header_signature: tuple[str, ...] | None = None

        for rows in row_groups:
            cleaned_rows = []
            for row in rows:
                cleaned_row = _clean_row(row)
                if any(cleaned_row):
                    cleaned_rows.append(cleaned_row)
            if not cleaned_rows:
                continue

            if not merged_rows:
                merged_rows.extend(cleaned_rows)
                merged_header_signature = _row_signature(cleaned_rows[0])
                continue

            current_header_signature = _row_signature(cleaned_rows[0])
            if (
                merged_header_signature is not None
                and current_header_signature == merged_header_signature
            ):
                merged_rows.extend(cleaned_rows[1:])
                continue

            merged_rows.extend(cleaned_rows)

        return merged_rows or None


def _clean_row(row: Sequence[object]) -> list[str]:
    return [" ".join(str(cell or "").split()).strip() for cell in row]


def _row_signature(row: Sequence[str]) -> tuple[str, ...]:
    return tuple(cell.casefold() for cell in row if cell)
