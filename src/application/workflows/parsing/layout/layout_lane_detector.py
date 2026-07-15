from dataclasses import dataclass

from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)


@dataclass(frozen=True, slots=True)
class LayoutLaneDetection:
    lane_count: int
    split_x: float | None = None


class LayoutLaneDetector:
    _MAX_COLUMN_WIDTH_RATIO = 0.72
    _MIN_GAP_RATIO = 0.05
    _LEFT_BOUNDARY_RATIO = 0.56
    _RIGHT_BOUNDARY_RATIO = 0.44
    _MIN_SIDE_CANDIDATES = 2

    def detect(
        self,
        *,
        page_width: float | None,
        candidates: list[PageLayoutCandidate],
    ) -> LayoutLaneDetection:
        if page_width is None or page_width <= 0:
            return LayoutLaneDetection(lane_count=1)

        usable = [
            candidate
            for candidate in candidates
            if candidate.bbox is not None
            and (candidate.width() or 0.0) <= page_width * self._MAX_COLUMN_WIDTH_RATIO
        ]
        if len(usable) < self._MIN_SIDE_CANDIDATES * 2:
            return LayoutLaneDetection(lane_count=1)

        left = [
            candidate
            for candidate in usable
            if candidate.bbox is not None
            and candidate.bbox.x2 <= page_width * self._LEFT_BOUNDARY_RATIO
        ]
        right = [
            candidate
            for candidate in usable
            if candidate.bbox is not None
            and candidate.bbox.x1 >= page_width * self._RIGHT_BOUNDARY_RATIO
        ]
        if (
            len(left) < self._MIN_SIDE_CANDIDATES
            or len(right) < self._MIN_SIDE_CANDIDATES
        ):
            return LayoutLaneDetection(lane_count=1)

        left_max = max(candidate.bbox.x2 for candidate in left if candidate.bbox is not None)
        right_min = min(
            candidate.bbox.x1 for candidate in right if candidate.bbox is not None
        )
        gap = right_min - left_max
        if gap < page_width * self._MIN_GAP_RATIO:
            return LayoutLaneDetection(lane_count=1)

        return LayoutLaneDetection(
            lane_count=2,
            split_x=(left_max + right_min) / 2.0,
        )
