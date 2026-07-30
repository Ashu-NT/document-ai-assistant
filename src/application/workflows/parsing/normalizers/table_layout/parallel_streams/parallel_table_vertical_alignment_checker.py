from __future__ import annotations

from src.domain.assets import TableCellSpan


class ParallelTableVerticalAlignmentChecker:
    _MIN_VERTICAL_OVERLAP_RATIO = 0.2
    _MAX_HEADER_TOP_DELTA = 96.0

    def are_compatible(
        self,
        groups: list[list[TableCellSpan]],
    ) -> bool:
        if len(groups) < 2:
            return False

        bands = [self._band(group) for group in groups]
        if any(band is None for band in bands):
            return False

        resolved_bands = [band for band in bands if band is not None]
        reference = resolved_bands[0]
        return all(
            self._bands_overlap(reference, candidate)
            and self._header_tops_are_close(reference, candidate)
            for candidate in resolved_bands[1:]
        )

    @staticmethod
    def _band(
        group: list[TableCellSpan],
    ) -> tuple[float, float, float] | None:
        bboxes = [span.bbox for span in group if span.bbox is not None]
        if not bboxes:
            return None
        min_row_start = min(span.row_start for span in group)
        top = min(bbox.y1 for bbox in bboxes)
        bottom = max(bbox.y2 for bbox in bboxes)
        header_top = min(
            span.bbox.y1
            for span in group
            if span.bbox is not None and span.row_start == min_row_start
        )
        return (top, bottom, header_top)

    def _bands_overlap(
        self,
        left: tuple[float, float, float],
        right: tuple[float, float, float],
    ) -> bool:
        overlap = max(0.0, min(left[1], right[1]) - max(left[0], right[0]))
        height = min(max(1.0, left[1] - left[0]), max(1.0, right[1] - right[0]))
        return (overlap / height) >= self._MIN_VERTICAL_OVERLAP_RATIO

    def _header_tops_are_close(
        self,
        left: tuple[float, float, float],
        right: tuple[float, float, float],
    ) -> bool:
        return abs(left[2] - right[2]) <= self._MAX_HEADER_TOP_DELTA
