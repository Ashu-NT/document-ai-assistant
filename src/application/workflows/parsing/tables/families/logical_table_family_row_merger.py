from __future__ import annotations

from typing import Sequence

from src.application.workflows.parsing.tables.structure.table_header_path_builder import (
    TableHeaderPathBuilder,
)
from src.application.workflows.parsing.tables.family_resolution.table_header_compatibility_matcher import (
    TableHeaderCompatibilityMatcher,
)
from src.domain.assets import TableAsset


class LogicalTableFamilyRowMerger:
    def __init__(
        self,
        *,
        header_compatibility_matcher: TableHeaderCompatibilityMatcher | None = None,
        header_path_builder: TableHeaderPathBuilder | None = None,
    ) -> None:
        self.header_compatibility_matcher = (
            header_compatibility_matcher or TableHeaderCompatibilityMatcher()
        )
        self.header_path_builder = header_path_builder or TableHeaderPathBuilder()

    def merge_tables(self, tables: Sequence[TableAsset]) -> list[list[str]] | None:
        merged_rows: list[list[str]] = []
        previous_table: TableAsset | None = None

        for table in tables:
            cleaned_rows = _clean_rows(table.rows)
            if not cleaned_rows:
                continue
            if not merged_rows:
                merged_rows.extend(cleaned_rows)
                previous_table = table
                continue

            if (
                previous_table is not None
                and self.header_compatibility_matcher.are_compatible(previous_table, table)
            ):
                merged_rows.extend(self._drop_repeated_header_rows(table, cleaned_rows))
                previous_table = table
                continue

            current_signature = _row_signature(cleaned_rows[0])
            merged_signature = _row_signature(merged_rows[0]) if merged_rows else ()
            if current_signature and current_signature == merged_signature:
                merged_rows.extend(cleaned_rows[1:])
            else:
                merged_rows.extend(cleaned_rows)
            previous_table = table

        return merged_rows or None

    def merge_row_groups(
        self,
        row_groups: Sequence[Sequence[Sequence[str]]],
    ) -> list[list[str]] | None:
        merged_rows: list[list[str]] = []
        previous_table: TableAsset | None = None

        for rows in row_groups:
            cleaned_rows = _clean_rows(rows)
            if not cleaned_rows:
                continue
            current_table = self._temporary_table(cleaned_rows)

            if not merged_rows:
                merged_rows.extend(cleaned_rows)
                previous_table = current_table
                continue

            if (
                previous_table is not None
                and self.header_compatibility_matcher.are_compatible(
                    previous_table,
                    current_table,
                )
            ):
                merged_rows.extend(self._drop_repeated_header_rows(current_table, cleaned_rows))
                previous_table = current_table
                continue

            current_signature = _row_signature(cleaned_rows[0])
            merged_signature = _row_signature(merged_rows[0]) if merged_rows else ()
            if current_signature and current_signature == merged_signature:
                merged_rows.extend(cleaned_rows[1:])
                previous_table = current_table
                continue

            merged_rows.extend(cleaned_rows)
            previous_table = current_table

        return merged_rows or None

    def _drop_repeated_header_rows(
        self,
        table: TableAsset,
        cleaned_rows: list[list[str]],
    ) -> list[list[str]]:
        header_row_count = self._header_row_count(table)
        if len(cleaned_rows) <= header_row_count:
            return []
        return cleaned_rows[header_row_count:]

    def _header_row_count(self, table: TableAsset) -> int:
        return min(
            max(1, self.header_path_builder.resolve_header_row_count(table)),
            len(table.rows),
        )

    @staticmethod
    def _temporary_table(rows: list[list[str]]) -> TableAsset:
        return TableAsset(
            table_id="logical_table_family_merge",
            document_id="logical_table_family_merge",
            markdown="",
            rows=rows,
        )


def _clean_row(row: Sequence[object]) -> list[str]:
    return [" ".join(str(cell or "").split()).strip() for cell in row]


def _clean_rows(rows: Sequence[Sequence[object]]) -> list[list[str]]:
    cleaned_rows: list[list[str]] = []
    for row in rows:
        cleaned_row = _clean_row(row)
        if any(cleaned_row):
            cleaned_rows.append(cleaned_row)
    return cleaned_rows


def _row_signature(row: Sequence[str]) -> tuple[str, ...]:
    return tuple(cell.casefold() for cell in row if cell)
