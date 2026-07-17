from collections import defaultdict

from src.application.workflows.parsing.layout.layout_lane_detector import (
    LayoutLaneDetection,
)
from src.application.workflows.parsing.layout.layout_reading_order_resolver import (
    LayoutReadingOrderResolver,
)
from src.application.workflows.parsing.layout.layout_region_segmenter import (
    LayoutRegionSegmenter,
)
from src.application.workflows.parsing.layout.models.layout_region_role import (
    LayoutRegionRole,
)
from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.application.workflows.parsing.layout.models.page_layout_region import (
    PageLayoutRegion,
)
from src.domain.common import BoundingBox


class LayoutRegionBuilder:
    _FULL_WIDTH_RATIO = 0.8

    def __init__(
        self,
        *,
        reading_order_resolver: LayoutReadingOrderResolver | None = None,
        region_segmenter: LayoutRegionSegmenter | None = None,
    ) -> None:
        self.reading_order_resolver = (
            reading_order_resolver or LayoutReadingOrderResolver()
        )
        self.region_segmenter = region_segmenter or LayoutRegionSegmenter()

    def build(
        self,
        *,
        page_number: int,
        page_width: float | None,
        detection: LayoutLaneDetection,
        is_front_matter: bool,
        candidates: list[PageLayoutCandidate],
    ) -> tuple[PageLayoutRegion, ...]:
        grouped: dict[str, list[PageLayoutCandidate]] = defaultdict(list)
        lane_meta: dict[str, int | None] = {}

        for candidate in candidates:
            lane_index = self._resolve_lane_index(
                candidate=candidate,
                page_width=page_width,
                detection=detection,
            )
            region_key = "full" if lane_index is None else f"lane:{lane_index}"
            grouped[region_key].append(candidate)
            lane_meta[region_key] = lane_index

        # All lane groups on this page form one shared left-to-right column
        # bank: they must never be reordered relative to EACH OTHER by raw
        # vertical position, since that only reflects an incidental
        # difference in exactly where each column's content happens to
        # start (a picture above one column but not the other, etc.), not
        # true reading order. Only lane_index should decide their relative
        # order, so both lanes are anchored to one shared top_y (the
        # earliest position across either lane) and lane_index breaks the
        # tie. "full" (full-width) groups keep sorting by their own actual
        # position, so headings/footers still interleave correctly before
        # or after the column bank.
        shared_lane_top_y = self._shared_lane_top_y(grouped)

        regions: list[PageLayoutRegion] = []
        for region_key, items in sorted(
            grouped.items(),
            key=lambda entry: self._sort_region_group(
                entry,
                shared_lane_top_y=shared_lane_top_y,
                lane_meta=lane_meta,
            ),
        ):
            ordered_items = self.reading_order_resolver.sort_candidates(items)
            segments = self.region_segmenter.segment(ordered_items)
            lane_index = lane_meta[region_key]
            for segment_index, segment in enumerate(segments):
                role_value = self._resolve_role(
                    candidate=segment[0],
                    lane_index=lane_index,
                    lane_count=detection.lane_count,
                    is_front_matter=is_front_matter,
                )
                region_items = list(segment)
                reading_order = self.reading_order_resolver.build_reading_order(region_items)
                regions.append(
                    PageLayoutRegion(
                        region_id=self._build_region_id(
                            page_number=page_number,
                            lane_index=lane_index,
                            segment_index=segment_index,
                            segment_total=len(segments),
                        ),
                        page_number=page_number,
                        role=LayoutRegionRole(role_value),
                        lane_index=lane_index,
                        lane_count=detection.lane_count,
                        bbox=self._merge_bbox(region_items),
                        element_refs=tuple(item.element_ref for item in region_items),
                        reading_order_by_element_ref=reading_order,
                    )
                )
        return tuple(regions)

    def _resolve_lane_index(
        self,
        *,
        candidate: PageLayoutCandidate,
        page_width: float | None,
        detection: LayoutLaneDetection,
    ) -> int | None:
        if detection.lane_count <= 1 or detection.split_x is None or candidate.bbox is None:
            return 0

        candidate_width = candidate.width() or 0.0
        if page_width and candidate_width >= page_width * self._FULL_WIDTH_RATIO:
            return None
        if candidate.spans_split(detection.split_x):
            return None

        center_x = candidate.center_x()
        if center_x is None:
            return None
        return 0 if center_x <= detection.split_x else 1

    @staticmethod
    def _resolve_role(
        *,
        candidate: PageLayoutCandidate,
        lane_index: int | None,
        lane_count: int,
        is_front_matter: bool,
    ) -> str:
        label = candidate.label.strip().lower()
        if is_front_matter:
            return LayoutRegionRole.FRONT_MATTER.value
        if "table" in label or label == "document_index":
            return LayoutRegionRole.TABLE_REGION.value
        if "picture" in label or "image" in label or "figure" in label:
            return LayoutRegionRole.PICTURE_REGION.value
        if lane_count > 1 and lane_index is None:
            return LayoutRegionRole.FULL_WIDTH.value
        if lane_count > 1:
            return LayoutRegionRole.PARALLEL_COLUMN.value
        return LayoutRegionRole.BODY_FLOW.value

    @staticmethod
    def _build_region_id(
        *,
        page_number: int,
        lane_index: int | None,
        segment_index: int,
        segment_total: int,
    ) -> str:
        base = (
            f"page_{page_number}:full"
            if lane_index is None
            else f"page_{page_number}:lane_{lane_index + 1}"
        )
        if segment_total <= 1:
            return base
        return f"{base}:region_{segment_index + 1}"

    @staticmethod
    def _shared_lane_top_y(grouped: dict[str, list[PageLayoutCandidate]]) -> float:
        lane_top_ys = [
            LayoutRegionBuilder._group_top_y(items)
            for key, items in grouped.items()
            if key != "full"
        ]
        return min(lane_top_ys, default=0.0)

    @staticmethod
    def _group_top_y(candidates: list[PageLayoutCandidate]) -> float:
        return min(
            (
                candidate.top_y()
                for candidate in candidates
                if candidate.top_y() is not None
            ),
            default=0.0,
        )

    @staticmethod
    def _sort_region_group(
        item: tuple[str, list[PageLayoutCandidate]],
        *,
        shared_lane_top_y: float,
        lane_meta: dict[str, int | None],
    ) -> tuple[float, int, int]:
        key, candidates = item
        if key == "full":
            return (LayoutRegionBuilder._group_top_y(candidates), 0, 0)
        lane_index = lane_meta[key] or 0
        return (shared_lane_top_y, 1, lane_index)

    @staticmethod
    def _merge_bbox(candidates: list[PageLayoutCandidate]) -> BoundingBox | None:
        bboxes = [candidate.bbox for candidate in candidates if candidate.bbox is not None]
        if not bboxes:
            return None
        return BoundingBox(
            x1=min(bbox.x1 for bbox in bboxes),
            y1=min(bbox.y1 for bbox in bboxes),
            x2=max(bbox.x2 for bbox in bboxes),
            y2=max(bbox.y2 for bbox in bboxes),
        )
