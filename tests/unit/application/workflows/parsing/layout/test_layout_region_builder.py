from src.application.workflows.parsing.layout.layout_lane_detector import (
    LayoutLaneDetection,
)
from src.application.workflows.parsing.layout.layout_region_builder import (
    LayoutRegionBuilder,
)
from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.domain.common import BoundingBox


def _candidate(
    *,
    element_ref: str,
    bbox: BoundingBox,
    label: str = "text",
    text: str | None = None,
) -> PageLayoutCandidate:
    return PageLayoutCandidate(
        element_ref=element_ref,
        page_number=1,
        bbox=bbox,
        label=label,
        text=text,
        content_layer="body",
    )


def test_build_orders_left_lane_before_right_lane_when_columns_start_at_same_height() -> (
    None
):
    candidates = [
        _candidate(element_ref="left_1", bbox=BoundingBox(56, 100, 300, 150)),
        _candidate(element_ref="right_1", bbox=BoundingBox(452, 100, 600, 150)),
    ]
    detection = LayoutLaneDetection(lane_count=2, split_x=376.0)

    regions = LayoutRegionBuilder().build(
        page_number=1,
        page_width=800,
        detection=detection,
        is_front_matter=False,
        candidates=candidates,
    )

    assert [region.element_refs[0] for region in regions] == ["left_1", "right_1"]


def test_build_still_orders_left_lane_before_right_lane_when_right_column_starts_higher() -> (
    None
):
    # Regression guard for a real bug: the right column's content starting
    # a bit higher on the page than the left column's (a common, incidental
    # layout variance -- e.g. one column has a picture above its text and
    # the other doesn't) used to flip the whole column's reading order,
    # putting the right column before the left one entirely.
    candidates = [
        _candidate(element_ref="right_1", bbox=BoundingBox(452, 100, 600, 150)),
        _candidate(element_ref="right_2", bbox=BoundingBox(452, 160, 600, 200)),
        _candidate(element_ref="left_1", bbox=BoundingBox(56, 180, 300, 230)),
        _candidate(element_ref="left_2", bbox=BoundingBox(56, 240, 300, 280)),
    ]
    detection = LayoutLaneDetection(lane_count=2, split_x=376.0)

    regions = LayoutRegionBuilder().build(
        page_number=27,
        page_width=800,
        detection=detection,
        is_front_matter=False,
        candidates=candidates,
    )

    ordered_refs = [ref for region in regions for ref in region.element_refs]
    assert ordered_refs == ["left_1", "left_2", "right_1", "right_2"]


def test_build_interleaves_full_width_heading_before_the_column_bank() -> None:
    candidates = [
        _candidate(
            element_ref="heading",
            bbox=BoundingBox(20, 10, 780, 40),
            label="section_header",
        ),
        _candidate(element_ref="right_1", bbox=BoundingBox(452, 100, 600, 150)),
        _candidate(element_ref="left_1", bbox=BoundingBox(56, 180, 300, 230)),
    ]
    detection = LayoutLaneDetection(lane_count=2, split_x=376.0)

    regions = LayoutRegionBuilder().build(
        page_number=1,
        page_width=800,
        detection=detection,
        is_front_matter=False,
        candidates=candidates,
    )

    ordered_refs = [ref for region in regions for ref in region.element_refs]
    assert ordered_refs == ["heading", "left_1", "right_1"]


def test_build_returns_single_region_for_single_column_page() -> None:
    candidates = [
        _candidate(element_ref="text_1", bbox=BoundingBox(20, 100, 780, 150)),
        _candidate(element_ref="text_2", bbox=BoundingBox(20, 160, 780, 200)),
    ]
    detection = LayoutLaneDetection(lane_count=1)

    regions = LayoutRegionBuilder().build(
        page_number=1,
        page_width=800,
        detection=detection,
        is_front_matter=False,
        candidates=candidates,
    )

    ordered_refs = [ref for region in regions for ref in region.element_refs]
    assert ordered_refs == ["text_1", "text_2"]
