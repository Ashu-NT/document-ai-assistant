from __future__ import annotations

import re
from dataclasses import dataclass

from src.domain.assets import TableAsset
from src.domain.common import BoundingBox
from src.domain.elements import CanonicalElement

_REGION_PATTERN = re.compile(
    r"^(?P<base>page_\d+:(?:lane_\d+|full))(?::region_(?P<index>\d+))?$"
)


@dataclass(frozen=True, slots=True)
class _RegionDescriptor:
    region_id: str | None
    region_role: str | None
    lane_index: int | None
    lane_count: int | None
    page_order: int | None
    bbox: BoundingBox | None


class SamePageTableRegionCompatibilityChecker:
    _MIN_HORIZONTAL_OVERLAP_RATIO = 0.45
    _VERTICAL_TOLERANCE = 24.0

    def are_compatible(
        self,
        *,
        previous: CanonicalElement,
        current: CanonicalElement,
        previous_table: TableAsset,
        current_table: TableAsset,
    ) -> bool:
        previous_descriptor = self._descriptor(previous, previous_table)
        current_descriptor = self._descriptor(current, current_table)

        if (
            previous_descriptor.region_id
            and current_descriptor.region_id
            and previous_descriptor.region_id == current_descriptor.region_id
        ):
            return True

        if not self._lanes_are_compatible(previous_descriptor, current_descriptor):
            return False
        if not self._same_region_stream(previous_descriptor, current_descriptor):
            return False
        if not self._roles_are_compatible(previous_descriptor, current_descriptor):
            return False
        if not self._page_order_increases(previous_descriptor, current_descriptor):
            return False
        return self._bboxes_look_stacked(previous_descriptor, current_descriptor)

    @staticmethod
    def _descriptor(
        element: CanonicalElement,
        table: TableAsset,
    ) -> _RegionDescriptor:
        extra = dict(element.parser_metadata.extra or {}) if element.parser_metadata else {}
        return _RegionDescriptor(
            region_id=table.layout_region_id,
            region_role=table.layout_region_role,
            lane_index=table.layout_lane_index,
            lane_count=table.layout_lane_count,
            page_order=SamePageTableRegionCompatibilityChecker._coerce_int(
                extra.get("layout_page_order")
            ),
            bbox=SamePageTableRegionCompatibilityChecker._bbox_from_data(
                extra.get("layout_region_bbox")
            ),
        )

    @staticmethod
    def _lanes_are_compatible(
        previous: _RegionDescriptor,
        current: _RegionDescriptor,
    ) -> bool:
        if max(previous.lane_count or 0, current.lane_count or 0) <= 1:
            return True
        if previous.lane_index is None or current.lane_index is None:
            return False
        return previous.lane_index == current.lane_index

    def _same_region_stream(
        self,
        previous: _RegionDescriptor,
        current: _RegionDescriptor,
    ) -> bool:
        previous_parts = self._region_parts(previous.region_id)
        current_parts = self._region_parts(current.region_id)
        if previous_parts is None or current_parts is None:
            return False
        previous_base, previous_index = previous_parts
        current_base, current_index = current_parts
        return previous_base == current_base and current_index == previous_index + 1

    @staticmethod
    def _roles_are_compatible(
        previous: _RegionDescriptor,
        current: _RegionDescriptor,
    ) -> bool:
        if previous.region_role and current.region_role:
            return previous.region_role == current.region_role == "table_region"
        return True

    @staticmethod
    def _page_order_increases(
        previous: _RegionDescriptor,
        current: _RegionDescriptor,
    ) -> bool:
        if previous.page_order is None or current.page_order is None:
            return True
        return current.page_order > previous.page_order

    def _bboxes_look_stacked(
        self,
        previous: _RegionDescriptor,
        current: _RegionDescriptor,
    ) -> bool:
        if previous.bbox is None or current.bbox is None:
            return True
        overlap_ratio = self._horizontal_overlap_ratio(previous.bbox, current.bbox)
        if overlap_ratio < self._MIN_HORIZONTAL_OVERLAP_RATIO:
            return False
        return current.bbox.y1 >= previous.bbox.y2 - self._VERTICAL_TOLERANCE

    @staticmethod
    def _horizontal_overlap_ratio(left: BoundingBox, right: BoundingBox) -> float:
        overlap = max(0.0, min(left.x2, right.x2) - max(left.x1, right.x1))
        width = min(max(1.0, left.x2 - left.x1), max(1.0, right.x2 - right.x1))
        return overlap / width

    @staticmethod
    def _region_parts(region_id: str | None) -> tuple[str, int] | None:
        if not region_id:
            return None
        match = _REGION_PATTERN.match(region_id.strip())
        if match is None:
            return None
        return match.group("base"), int(match.group("index") or "1")

    @staticmethod
    def _coerce_int(value: object) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _bbox_from_data(value: object) -> BoundingBox | None:
        if not isinstance(value, dict):
            return None
        try:
            return BoundingBox(
                x1=float(value["x1"]),
                y1=float(value["y1"]),
                x2=float(value["x2"]),
                y2=float(value["y2"]),
            )
        except (KeyError, TypeError, ValueError):
            return None
