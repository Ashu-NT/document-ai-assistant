from __future__ import annotations

from typing import Iterable, Sequence

from src.application.workflows.parsing.tables.families.logical_table_family_row_merger import (
    LogicalTableFamilyRowMerger,
)
from src.domain.assets import AssetMetadata, TableAsset


class LogicalTableFamilyAssetComposer:
    def __init__(
        self,
        *,
        row_merger: LogicalTableFamilyRowMerger | None = None,
    ) -> None:
        self.row_merger = row_merger or LogicalTableFamilyRowMerger()

    def compose(
        self,
        tables: Sequence[TableAsset],
        *,
        family_id: str | None = None,
    ) -> TableAsset | None:
        qualifying_tables = [table for table in tables if table.has_content() or table.rows]
        if not qualifying_tables:
            return None

        lead_table = qualifying_tables[0]
        merged_rows = self.row_merger.merge_tables(qualifying_tables) or [
            list(row) for row in lead_table.rows
        ]
        merged_markdown = self._merge_markdown(qualifying_tables) or lead_table.markdown
        metadata = AssetMetadata(
            caption=self._first_non_empty(table.metadata.caption for table in qualifying_tables),
            nearby_text=self._merge_nearby_text(qualifying_tables),
        )
        resolved_family_id = (
            family_id
            or lead_table.logical_table_family_id
            or (lead_table.table_id if len(qualifying_tables) == 1 else None)
        )
        return TableAsset(
            table_id=resolved_family_id or lead_table.table_id,
            document_id=lead_table.document_id,
            markdown=merged_markdown,
            parent_section_id=self._first_non_empty(
                table.parent_section_id for table in qualifying_tables
            ),
            rows=merged_rows,
            row_count=len(merged_rows) or None,
            column_count=max((len(row) for row in merged_rows), default=0) or None,
            logical_table_family_id=resolved_family_id,
            family_index=1,
            family_total=len(qualifying_tables),
            continuation_role="single" if len(qualifying_tables) == 1 else "merged",
            normalized_header_signature=self._first_non_empty(
                table.normalized_header_signature for table in qualifying_tables
            ),
            table_category=self._first_non_empty(
                table.table_category for table in qualifying_tables
            ),
            table_category_confidence=self._first_non_none(
                table.table_category_confidence for table in qualifying_tables
            ),
            table_shape=self._first_non_empty(table.table_shape for table in qualifying_tables),
            table_structure_quality=self._first_non_none(
                table.table_structure_quality for table in qualifying_tables
            ),
            header_paths=self._merge_header_paths(qualifying_tables),
            axis_summary=self._merge_axis_summary(qualifying_tables),
            signals=frozenset(
                signal
                for table in qualifying_tables
                for signal in table.signals
                if str(signal).strip()
            ),
            local_reading_order=self._first_non_empty(
                table.local_reading_order for table in qualifying_tables
            ),
            layout_region_role=self._first_non_empty(
                table.layout_region_role for table in qualifying_tables
            ),
            layout_lane_count=self._first_non_none(
                table.layout_lane_count for table in qualifying_tables
            ),
            page_orientation=self._first_non_empty(
                table.page_orientation for table in qualifying_tables
            ),
            metadata=metadata,
        )

    @staticmethod
    def _merge_markdown(tables: Sequence[TableAsset]) -> str:
        parts = [table.markdown.strip() for table in tables if table.markdown.strip()]
        return "\n\n".join(parts)

    @staticmethod
    def _merge_nearby_text(tables: Sequence[TableAsset]) -> str | None:
        seen: set[str] = set()
        parts: list[str] = []
        for table in tables:
            cleaned = str(table.metadata.nearby_text or "").strip()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            parts.append(cleaned)
        if not parts:
            return None
        return "\n\n".join(parts)

    @staticmethod
    def _merge_header_paths(tables: Sequence[TableAsset]) -> list[list[str]]:
        merged: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()
        for table in tables:
            for path in table.header_paths:
                cleaned = tuple(
                    str(part).strip() for part in path if str(part).strip()
                )
                if not cleaned or cleaned in seen:
                    continue
                seen.add(cleaned)
                merged.append(list(cleaned))
        return merged

    @staticmethod
    def _merge_axis_summary(tables: Sequence[TableAsset]) -> dict[str, str]:
        merged: dict[str, str] = {}
        for table in tables:
            for key, value in table.axis_summary.items():
                cleaned_key = str(key).strip()
                cleaned_value = str(value).strip()
                if cleaned_key and cleaned_value and cleaned_key not in merged:
                    merged[cleaned_key] = cleaned_value
        return merged

    @staticmethod
    def _first_non_empty(values: Iterable[str | None]) -> str | None:
        for value in values:
            cleaned = str(value or "").strip()
            if cleaned:
                return cleaned
        return None

    @staticmethod
    def _first_non_none(values: Iterable[object]) -> object | None:
        for value in values:
            if value is not None:
                return value
        return None
