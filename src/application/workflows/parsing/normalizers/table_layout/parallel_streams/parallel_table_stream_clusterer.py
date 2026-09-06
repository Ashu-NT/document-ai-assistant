from __future__ import annotations

from src.config.logging import get_logger
from src.domain.assets import TableCellSpan

_logger = get_logger(__name__)


class ParallelTableStreamClusterer:
    def cluster(
        self,
        spans: list[TableCellSpan],
        *,
        page_lane_count: int | None = None,
    ) -> list[list[TableCellSpan]]:
        bounded = self._bounded_single_page_spans(spans)
        if len(bounded) < 6:
            return self._log_disagreement_and_return([], page_lane_count=page_lane_count)

        sorted_spans = sorted(bounded, key=self._center_x)
        page_width = max(span.bbox.x2 for span in sorted_spans if span.bbox is not None) - min(
            span.bbox.x1 for span in sorted_spans if span.bbox is not None
        )
        widths = [
            max(1.0, span.bbox.x2 - span.bbox.x1)
            for span in sorted_spans
            if span.bbox is not None
        ]
        gap_threshold = max(page_width * 0.12, self._median(widths) * 1.6, 36.0)

        clusters: list[list[TableCellSpan]] = [[sorted_spans[0]]]
        previous_center = self._center_x(sorted_spans[0])
        for span in sorted_spans[1:]:
            center = self._center_x(span)
            if center - previous_center > gap_threshold:
                clusters.append([span])
            else:
                clusters[-1].append(span)
            previous_center = center

        result = [cluster for cluster in clusters if len(cluster) >= 3]
        return self._log_disagreement_and_return(result, page_lane_count=page_lane_count)

    @staticmethod
    def _log_disagreement_and_return(
        result: list[list[TableCellSpan]],
        *,
        page_lane_count: int | None,
    ) -> list[list[TableCellSpan]]:
        if page_lane_count is not None and len(result) != page_lane_count:
            _logger.debug(
                "parallel_table_stream_lane_count_disagreement "
                "cell_cluster_count=%s page_lane_count=%s",
                len(result),
                page_lane_count,
            )
        return result

    @staticmethod
    def _bounded_single_page_spans(
        spans: list[TableCellSpan],
    ) -> list[TableCellSpan]:
        bounded = [
            span
            for span in spans
            if span.bbox is not None and span.page_number is not None
        ]
        page_numbers = {span.page_number for span in bounded if span.page_number is not None}
        if len(page_numbers) != 1:
            return []
        return bounded

    @staticmethod
    def mean_center_x(spans: list[TableCellSpan]) -> float:
        return sum(ParallelTableStreamClusterer._center_x(span) for span in spans) / max(
            1, len(spans)
        )

    @staticmethod
    def _center_x(span: TableCellSpan) -> float:
        bbox = span.bbox
        if bbox is None:
            return 0.0
        return (bbox.x1 + bbox.x2) / 2.0

    @staticmethod
    def _median(values: list[float]) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2 == 1:
            return ordered[middle]
        return (ordered[middle - 1] + ordered[middle]) / 2.0
