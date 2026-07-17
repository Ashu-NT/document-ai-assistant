from __future__ import annotations

from dataclasses import replace

from src.application.workflows.parsing.normalizers.docling_table_row_repairer import (
    DoclingTableRowRepairer,
)
from src.application.workflows.parsing.normalizers.table_layout.parallel_table_quality_evaluator import (
    ParallelTableQualityEvaluator,
)
from src.application.workflows.parsing.normalizers.table_layout.parallel_table_stream_clusterer import (
    ParallelTableStreamClusterer,
)
from src.application.workflows.parsing.normalizers.table_layout.docling_table_raw_row_builder import (
    DoclingTableRawRowBuilder,
)
from src.application.workflows.parsing.normalizers.table_layout.table_reconstruction_result import (
    TableReconstructionResult,
)
from src.domain.assets import TableCellSpan


class DoclingParallelTableReconstructor:
    def __init__(
        self,
        *,
        clusterer: ParallelTableStreamClusterer | None = None,
        quality_evaluator: ParallelTableQualityEvaluator | None = None,
        raw_row_builder: DoclingTableRawRowBuilder | None = None,
        row_repairer: DoclingTableRowRepairer | None = None,
    ) -> None:
        self.clusterer = clusterer or ParallelTableStreamClusterer()
        self.quality_evaluator = quality_evaluator or ParallelTableQualityEvaluator()
        self.raw_row_builder = raw_row_builder or DoclingTableRawRowBuilder()
        self.row_repairer = row_repairer or DoclingTableRowRepairer()

    def reconstruct(
        self,
        spans: list[TableCellSpan],
        *,
        page_lane_count: int | None = None,
    ) -> TableReconstructionResult | None:
        lane_groups = self.clusterer.cluster(spans, page_lane_count=page_lane_count)
        if len(lane_groups) < 2:
            return None

        combined_rows = self.row_repairer.repair_rows(
            self.raw_row_builder.build_rows(spans),
            cell_spans=spans,
        )
        reconstructed_groups = self._reconstruct_groups(lane_groups)
        if len(reconstructed_groups) < 2:
            return None

        combined_density = self.quality_evaluator.density(combined_rows)
        average_density = sum(
            self.quality_evaluator.density(rows)
            for _, rows, _ in reconstructed_groups
        ) / len(reconstructed_groups)
        combined_score = self.quality_evaluator.score(combined_rows)
        average_score = sum(
            score for _, _, score in reconstructed_groups
        ) / len(reconstructed_groups)
        ordered_groups = [
            rows
            for _, rows, _ in sorted(reconstructed_groups, key=lambda item: item[0])
        ]
        if not self._should_use_parallel(
            combined_density=combined_density,
            average_density=average_density,
            combined_score=combined_score,
            average_score=average_score,
            ordered_groups=ordered_groups,
        ):
            return None

        primary_rows = self._resolve_primary_rows(ordered_groups, reconstructed_groups)
        return TableReconstructionResult(
            rows=primary_rows,
            cell_spans=spans,
            parallel_stream_rows=ordered_groups,
            local_reading_order="left_to_right_top_to_bottom",
            reconstruction_version="1",
        )

    def _reconstruct_groups(
        self,
        lane_groups: list[list[TableCellSpan]],
    ) -> list[tuple[float, list[list[str]], float]]:
        groups: list[tuple[float, list[list[str]], float]] = []
        for lane_spans in lane_groups:
            normalized_lane_spans = self._normalize_lane_spans(lane_spans)
            repaired_rows = self.row_repairer.repair_rows(
                self.raw_row_builder.build_rows(normalized_lane_spans),
                cell_spans=normalized_lane_spans,
            )
            if len(repaired_rows) < 2:
                continue
            score = self.quality_evaluator.score(repaired_rows)
            groups.append(
                (
                    self.clusterer.mean_center_x(lane_spans),
                    repaired_rows,
                    score,
                )
            )
        return groups

    @staticmethod
    def _normalize_lane_spans(
        lane_spans: list[TableCellSpan],
    ) -> list[TableCellSpan]:
        min_col = min((span.col_start for span in lane_spans), default=0)
        min_row = min((span.row_start for span in lane_spans), default=0)
        if min_col == 0 and min_row == 0:
            return lane_spans
        return [
            replace(
                span,
                col_start=span.col_start - min_col,
                col_end=span.col_end - min_col,
                row_start=span.row_start - min_row,
                row_end=span.row_end - min_row,
            )
            for span in lane_spans
        ]

    @staticmethod
    def _should_use_parallel(
        *,
        combined_density: float,
        average_density: float,
        combined_score: float,
        average_score: float,
        ordered_groups: list[list[list[str]]],
    ) -> bool:
        if DoclingParallelTableReconstructor._looks_like_repeated_header_streams(
            ordered_groups
        ):
            return True
        if average_density < combined_density + 0.18:
            return False
        if average_score < combined_score + 0.12:
            return False
        return combined_density <= 0.68

    def _resolve_primary_rows(
        self,
        ordered_groups: list[list[list[str]]],
        scored_groups: list[tuple[float, list[list[str]], float]],
    ) -> list[list[str]]:
        if self._headers_match(ordered_groups):
            header = list(ordered_groups[0][0])
            merged = [header]
            for rows in ordered_groups:
                merged.extend(rows[1:])
            return merged
        best_rows = max(scored_groups, key=lambda item: item[2])[1]
        return [list(row) for row in best_rows]

    @staticmethod
    def _headers_match(groups: list[list[list[str]]]) -> bool:
        signatures = [
            tuple(
                str(cell).strip().casefold()
                for cell in rows[0]
                if str(cell).strip()
            )
            for rows in groups
            if rows and rows[0]
        ]
        if len(signatures) != len(groups) or not signatures:
            return False
        first = signatures[0]
        return bool(first) and all(signature == first for signature in signatures[1:])

    @staticmethod
    def _looks_like_repeated_header_streams(groups: list[list[list[str]]]) -> bool:
        if len(groups) < 2 or not DoclingParallelTableReconstructor._headers_match(groups):
            return False
        widths = [len(rows[0]) for rows in groups if rows and rows[0]]
        if not widths or min(widths) < 2:
            return False
        row_counts = [len(rows) for rows in groups]
        return max(row_counts, default=0) >= 2
