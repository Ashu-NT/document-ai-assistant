from bisect import bisect_left
from dataclasses import replace

from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.application.workflows.parsing.builders.document_graph.source_location_factory import (
    SourceLocationFactory,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.domain.assets import (
    AssetMetadata,
    PictureAsset,
    TableAsset,
    TableCellSpan,
    TableParallelStream,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    compute_kept_column_indexes,
    drop_globally_empty_columns,
)
from src.shared.ids import IdGenerator


class ParsedAssetFactory:
    def __init__(self, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def build_table_asset(
        self,
        *,
        document_id: str,
        parent_section_id: str | None,
        parsed_element: ParsedCanonicalElement,
    ) -> tuple[str, TableAsset]:
        table_id = self.id_generator.new_id("table")
        rows, kept_column_indexes, original_width = self._clean_rows_with_column_map(
            parsed_element.metadata.get("table_rows")
        )
        cell_spans = TableCellSpan.list_from_data(
            parsed_element.metadata.get("table_cell_spans")
        )
        column_count = parsed_element.metadata.get("column_count")
        dropped_count = original_width - len(kept_column_indexes)
        if dropped_count > 0:
            cell_spans = self._remap_cell_spans(cell_spans, kept_column_indexes)
            if isinstance(column_count, int):
                column_count = column_count - dropped_count
        return (
            table_id,
            TableAsset(
                table_id=table_id,
                document_id=document_id,
                markdown=(
                    self._clean_multiline_text(
                        parsed_element.metadata.get("markdown")
                        or parsed_element.text
                    )
                    or ""
                ),
                parent_section_id=parent_section_id,
                rows=rows,
                parallel_stream_rows=self._clean_parallel_stream_rows(
                    parsed_element.metadata.get("table_parallel_stream_rows")
                ),
                parallel_stream_descriptors=TableParallelStream.list_from_data(
                    parsed_element.metadata.get("table_parallel_stream_descriptors")
                ),
                row_ids=self._build_row_ids(
                    table_id=table_id,
                    row_count=(
                        parsed_element.metadata.get("row_count")
                        or len(parsed_element.metadata.get("table_rows") or [])
                    ),
                ),
                cell_spans=cell_spans,
                row_count=parsed_element.metadata.get("row_count"),
                column_count=column_count,
                local_reading_order=self._clean_text(
                    parsed_element.metadata.get("table_local_reading_order")
                ),
                table_shape=self._clean_text(parsed_element.metadata.get("table_shape")),
                table_structure_quality=self._coerce_float(
                    parsed_element.metadata.get("table_structure_quality")
                ),
                header_paths=self._clean_header_paths(
                    parsed_element.metadata.get("table_header_paths_json")
                ),
                axis_summary=self._clean_axis_summary(
                    parsed_element.metadata.get("table_axis_summary")
                ),
                layout_region_id=self._clean_text(
                    parsed_element.metadata.get("layout_region_id")
                ),
                layout_region_role=self._clean_text(
                    parsed_element.metadata.get("layout_region_role")
                ),
                layout_lane_index=self._coerce_int(
                    parsed_element.metadata.get("layout_lane_index")
                ),
                layout_lane_count=self._coerce_int(
                    parsed_element.metadata.get("layout_lane_count")
                ),
                page_orientation=self._clean_text(
                    parsed_element.metadata.get("page_orientation")
                ),
                metadata=AssetMetadata(
                    source=SourceLocationFactory.from_parsed(parsed_element),
                    caption=parsed_element.metadata.get("caption"),
                ),
            ),
        )

    def build_picture_asset(
        self,
        *,
        document_id: str,
        parent_section_id: str | None,
        parsed_element: ParsedCanonicalElement,
    ) -> tuple[str, PictureAsset]:
        picture_id = self.id_generator.new_id("picture")
        return (
            picture_id,
            PictureAsset(
                picture_id=picture_id,
                document_id=document_id,
                parent_section_id=parent_section_id,
                image_path=parsed_element.metadata.get("image_path"),
                ocr_text=parsed_element.metadata.get("ocr_text"),
                ocr_confidence=self._coerce_float(
                    parsed_element.metadata.get("ocr_confidence")
                ),
                ocr_provider=self._clean_text(
                    parsed_element.metadata.get("ocr_provider")
                ),
                ocr_mode=self._clean_text(
                    parsed_element.metadata.get("ocr_mode")
                    or parsed_element.metadata.get("ocr_target_type")
                ),
                metadata=AssetMetadata(
                    source=SourceLocationFactory.from_parsed(parsed_element),
                    caption=parsed_element.metadata.get("caption")
                    or parsed_element.text,
                ),
            ),
        )

    @staticmethod
    def _build_row_ids(*, table_id: str, row_count: object) -> list[str]:
        if not isinstance(row_count, (int, float, str)):
            return []
        try:
            count = max(0, int(row_count))
        except (TypeError, ValueError):
            return []
        return [f"{table_id}:row:{index}" for index in range(count)]

    @staticmethod
    def _coerce_float(value: object) -> float | None:
        if not isinstance(value, (int, float, str)):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_int(value: object) -> int | None:
        if not isinstance(value, (int, float, str)):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _clean_header_paths(cls, value: object) -> list[list[str]]:
        if not isinstance(value, list):
            return []
        cleaned_paths: list[list[str]] = []
        for path in value:
            if not isinstance(path, list):
                continue
            cleaned_path = [cls._clean_text(part) or "" for part in path]
            cleaned_path = [part for part in cleaned_path if part]
            cleaned_paths.append(cleaned_path)
        return cleaned_paths

    @classmethod
    def _clean_axis_summary(cls, value: object) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        cleaned_summary: dict[str, str] = {}
        for key, raw_value in value.items():
            cleaned_key = cls._clean_text(key)
            cleaned_value = cls._clean_text(raw_value)
            if cleaned_key and cleaned_value:
                cleaned_summary[cleaned_key] = cleaned_value
        return cleaned_summary

    @staticmethod
    def _clean_text(value: object) -> str | None:
        text = repair_docling_text(str(value or "")).strip()
        return text or None

    @classmethod
    def _clean_multiline_text(cls, value: object) -> str | None:
        if value is None:
            return None
        lines = [
            repair_docling_text(str(line)).rstrip()
            for line in str(value).splitlines()
        ]
        text = "\n".join(lines).strip()
        return text or None

    @classmethod
    def _clean_rows_with_column_map(
        cls, rows: object
    ) -> tuple[list[list[str]], list[int], int]:
        if not isinstance(rows, list):
            return [], [], 0
        cleaned_rows: list[list[str]] = []
        for row in rows:
            if not isinstance(row, list):
                continue
            cleaned_rows.append(
                [
                    cls._clean_text(cell) or ""
                    for cell in row
                ]
            )
        original_width = max((len(row) for row in cleaned_rows), default=0)
        kept_column_indexes = compute_kept_column_indexes(cleaned_rows)
        return (
            drop_globally_empty_columns(cleaned_rows),
            kept_column_indexes,
            original_width,
        )

    @classmethod
    def _clean_parallel_stream_rows(cls, value: object) -> list[list[list[str]]]:
        if not isinstance(value, list):
            return []
        cleaned_streams: list[list[list[str]]] = []
        for stream_rows in value:
            if not isinstance(stream_rows, list):
                continue
            cleaned_rows, _, _ = cls._clean_rows_with_column_map(stream_rows)
            if cleaned_rows:
                cleaned_streams.append(cleaned_rows)
        return cleaned_streams

    @staticmethod
    def _remap_cell_spans(
        cell_spans: list[TableCellSpan],
        kept_column_indexes: list[int],
    ) -> list[TableCellSpan]:
        if not kept_column_indexes:
            return []
        remapped_spans: list[TableCellSpan] = []
        for span in cell_spans:
            new_col_start = bisect_left(kept_column_indexes, span.col_start)
            new_col_end = bisect_left(kept_column_indexes, span.col_end + 1) - 1
            if new_col_end < new_col_start:
                continue
            remapped_spans.append(
                replace(span, col_start=new_col_start, col_end=new_col_end)
            )
        return remapped_spans
