from __future__ import annotations

from collections import defaultdict

from src.application.workflows.parsing.normalizers.table_rows.docling_toc_table_row_reconstructor import (
    TOC_PAGE_NUMBER_PATTERN,
    DoclingTocTableRowReconstructor,
)
from src.application.workflows.parsing.normalizers.table_layout.parallel_streams.parallel_table_stream_clusterer import (
    ParallelTableStreamClusterer,
)
from src.application.workflows.parsing.normalizers.table_layout.parallel_streams.docling_table_raw_row_builder import (
    DoclingTableRawRowBuilder,
)
from src.domain.assets import TableCellSpan


class DoclingParallelTocReconstructor:
    def __init__(
        self,
        *,
        clusterer: ParallelTableStreamClusterer | None = None,
        raw_row_builder: DoclingTableRawRowBuilder | None = None,
        toc_reconstructor: DoclingTocTableRowReconstructor | None = None,
    ) -> None:
        self.clusterer = clusterer or ParallelTableStreamClusterer()
        self.raw_row_builder = raw_row_builder or DoclingTableRawRowBuilder()
        self.toc_reconstructor = toc_reconstructor or DoclingTocTableRowReconstructor()

    def reconstruct(self, spans: list[TableCellSpan]) -> list[list[str]] | None:
        grouped = self._group_by_page(spans)
        if not grouped:
            return None

        combined: list[list[str]] = []
        header: list[str] | None = None
        used_parallel_layout = False

        for page_number in sorted(grouped):
            page_rows, page_parallel = self._reconstruct_page(grouped[page_number])
            if not page_rows:
                continue
            used_parallel_layout = used_parallel_layout or page_parallel
            if header is None:
                header = page_rows[0]
                combined.append(header)
                combined.extend(page_rows[1:])
                continue
            if self._same_header(header, page_rows[0]):
                combined.extend(page_rows[1:])
            else:
                combined.extend(page_rows)

        if not used_parallel_layout or not combined:
            return None
        return combined

    def _reconstruct_page(
        self,
        spans: list[TableCellSpan],
    ) -> tuple[list[list[str]], bool]:
        lane_groups = self.clusterer.cluster(spans)
        if len(lane_groups) < 2:
            raw_rows = self.raw_row_builder.build_rows(spans)
            return self._reconstruct_toc_rows(raw_rows), False

        reconstructed_groups: list[tuple[float, list[list[str]]]] = []
        for lane_spans in lane_groups:
            raw_rows = self.raw_row_builder.build_rows(lane_spans)
            reconstructed = self._reconstruct_toc_rows(raw_rows)
            if self._looks_like_reconstructed_toc(raw_rows, reconstructed):
                reconstructed_groups.append(
                    (
                        self.clusterer.mean_center_x(lane_spans),
                        reconstructed,
                    )
                )

        if len(reconstructed_groups) < 2:
            raw_rows = self.raw_row_builder.build_rows(spans)
            return self._reconstruct_toc_rows(raw_rows), False

        ordered_groups = sorted(reconstructed_groups, key=lambda item: item[0])
        merged: list[list[str]] = [ordered_groups[0][1][0]]
        for _, rows in ordered_groups:
            if self._same_header(merged[0], rows[0]):
                merged.extend(rows[1:])
            else:
                merged.extend(rows)
        return merged, True

    @staticmethod
    def _group_by_page(
        spans: list[TableCellSpan],
    ) -> dict[int, list[TableCellSpan]]:
        grouped: dict[int, list[TableCellSpan]] = defaultdict(list)
        for span in spans:
            if span.page_number is None:
                return {}
            grouped[span.page_number].append(span)
        return grouped

    def _reconstruct_toc_rows(self, raw_rows: list[list[str]]) -> list[list[str]]:
        reconstructed = self.toc_reconstructor.reconstruct(raw_rows)
        if self._looks_like_reconstructed_toc(raw_rows, reconstructed):
            return reconstructed
        return raw_rows

    @staticmethod
    def _looks_like_reconstructed_toc(
        raw_rows: list[list[str]],
        reconstructed: list[list[str]],
    ) -> bool:
        if reconstructed == raw_rows or len(reconstructed) < 4:
            return False
        data_rows = reconstructed[1:]
        return bool(data_rows) and all(
            bool(row) and TOC_PAGE_NUMBER_PATTERN.fullmatch(str(row[-1]).strip())
            for row in data_rows
        )

    @staticmethod
    def _same_header(left: list[str], right: list[str]) -> bool:
        return len(left) == len(right) and all(
            str(a).strip() == str(b).strip()
            for a, b in zip(left, right, strict=False)
        )
