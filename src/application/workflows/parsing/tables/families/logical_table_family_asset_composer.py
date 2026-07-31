from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Sequence

from src.application.workflows.parsing.tables.families.logical_table_family_row_merger import (
    LogicalTableFamilyRowMerger,
)
from src.domain.assets import AssetMetadata, TableAsset, TableParallelStream


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
        parallel_stream_rows = self._merge_parallel_stream_rows(qualifying_tables)
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
            cell_spans=[span for table in qualifying_tables for span in table.cell_spans],
            parallel_stream_rows=parallel_stream_rows,
            parallel_stream_descriptors=self._merge_parallel_stream_descriptors(
                qualifying_tables,
                stream_rows=parallel_stream_rows,
            ),
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

    def _merge_parallel_stream_rows(
        self,
        tables: Sequence[TableAsset],
    ) -> list[list[list[str]]]:
        if not tables or not all(table.parallel_stream_rows for table in tables):
            return []
        stream_count = len(tables[0].parallel_stream_rows)
        if stream_count == 0:
            return []
        if all(len(table.parallel_stream_rows) == stream_count for table in tables):
            merged: list[list[list[str]]] = []
            for stream_index in range(stream_count):
                merged_rows = self.row_merger.merge_row_groups(
                    [table.parallel_stream_rows[stream_index] for table in tables]
                )
                if merged_rows:
                    merged.append(merged_rows)
            if merged:
                return merged
        return [
            [list(row) for row in stream_rows]
            for table in tables
            for stream_rows in table.parallel_stream_rows
        ]

    def _merge_parallel_stream_descriptors(
        self,
        tables: Sequence[TableAsset],
        *,
        stream_rows: Sequence[Sequence[Sequence[str]]],
    ) -> list[TableParallelStream]:
        if not stream_rows:
            return []
        if not all(table.parallel_stream_descriptors for table in tables):
            return []
        expected_stream_count = len(tables[0].parallel_stream_descriptors)
        if expected_stream_count == 0:
            return []
        if all(
            len(table.parallel_stream_descriptors) == expected_stream_count
            for table in tables
        ) and expected_stream_count == len(stream_rows):
            merged = [
                self._merge_stream_descriptor_group(
                    [
                        table.parallel_stream_descriptors[stream_index]
                        for table in tables
                    ],
                    stream_index=stream_index + 1,
                    merged_rows=stream_rows[stream_index],
                )
                for stream_index in range(expected_stream_count)
            ]
            return [item for item in merged if item is not None]
        flattened: list[TableParallelStream] = []
        for descriptor in (
            stream
            for table in tables
            for stream in table.parallel_stream_descriptors
        ):
            flattened.append(replace(descriptor, stream_index=len(flattened) + 1))
        return flattened

    @staticmethod
    def _merge_stream_descriptor_group(
        descriptors: Sequence[TableParallelStream],
        *,
        stream_index: int,
        merged_rows: Sequence[Sequence[str]],
    ) -> TableParallelStream | None:
        if not descriptors:
            return None
        page_numbers = [item.page_number for item in descriptors if item.page_number is not None]
        unique_page_numbers = set(page_numbers)
        bboxes = [item.bbox for item in descriptors if item.bbox is not None]
        centers = [item.center_x for item in descriptors if item.center_x is not None]
        return TableParallelStream(
            stream_index=stream_index,
            source_row_start=min(item.source_row_start for item in descriptors),
            source_row_end=max(item.source_row_end for item in descriptors),
            source_col_start=min(item.source_col_start for item in descriptors),
            source_col_end=max(item.source_col_end for item in descriptors),
            row_count=len(merged_rows),
            column_count=max((len(row) for row in merged_rows), default=0),
            page_number=(
                next(iter(unique_page_numbers))
                if len(unique_page_numbers) == 1
                else None
            ),
            center_x=(sum(centers) / len(centers)) if centers else None,
            bbox=(
                replace(
                    bboxes[0],
                    x1=min(item.x1 for item in bboxes),
                    y1=min(item.y1 for item in bboxes),
                    x2=max(item.x2 for item in bboxes),
                    y2=max(item.y2 for item in bboxes),
                )
                if bboxes and len(unique_page_numbers) <= 1
                else None
            ),
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
