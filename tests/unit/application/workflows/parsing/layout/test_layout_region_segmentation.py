from types import SimpleNamespace

from src.application.workflows.parsing.layout.page_layout_analyzer import (
    PageLayoutAnalyzer,
)
from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.domain.common import BoundingBox


def _raw_document_with_page_size(*, width: float, height: float) -> SimpleNamespace:
    return SimpleNamespace(
        pages={1: SimpleNamespace(size=SimpleNamespace(width=width, height=height))}
    )


def test_page_layout_analyzer_splits_same_lane_into_multiple_regions() -> None:
    analyzer = PageLayoutAnalyzer()
    metadata = analyzer.analyze_and_serialize(
        raw_document=_raw_document_with_page_size(width=1000, height=1400),
        candidates=[
            PageLayoutCandidate(
                element_ref="table_top_1",
                page_number=1,
                bbox=BoundingBox(x1=80, y1=1180, x2=920, y2=1280),
                label="table",
                text="top table row 1",
            ),
            PageLayoutCandidate(
                element_ref="table_top_2",
                page_number=1,
                bbox=BoundingBox(x1=80, y1=1060, x2=920, y2=1160),
                label="table",
                text="top table row 2",
            ),
            PageLayoutCandidate(
                element_ref="table_bottom_1",
                page_number=1,
                bbox=BoundingBox(x1=90, y1=690, x2=910, y2=780),
                label="table",
                text="bottom table row 1",
            ),
            PageLayoutCandidate(
                element_ref="table_bottom_2",
                page_number=1,
                bbox=BoundingBox(x1=90, y1=580, x2=910, y2=670),
                label="table",
                text="bottom table row 2",
            ),
        ],
    )

    assert metadata["table_top_1"]["layout_region_id"] == "page_1:lane_1:region_1"
    assert metadata["table_top_2"]["layout_region_id"] == "page_1:lane_1:region_1"
    assert metadata["table_bottom_1"]["layout_region_id"] == "page_1:lane_1:region_2"
    assert metadata["table_bottom_2"]["layout_region_id"] == "page_1:lane_1:region_2"


def test_page_layout_analyzer_splits_role_change_inside_same_lane() -> None:
    analyzer = PageLayoutAnalyzer()
    metadata = analyzer.analyze_and_serialize(
        raw_document=_raw_document_with_page_size(width=1000, height=1400),
        candidates=[
            PageLayoutCandidate(
                element_ref="body_text",
                page_number=1,
                bbox=BoundingBox(x1=90, y1=1080, x2=900, y2=1180),
                label="text",
                text="narrative",
            ),
            PageLayoutCandidate(
                element_ref="table_block",
                page_number=1,
                bbox=BoundingBox(x1=90, y1=880, x2=900, y2=1040),
                label="table",
                text="table",
            ),
        ],
    )

    assert metadata["body_text"]["layout_region_id"] == "page_1:lane_1:region_1"
    assert metadata["table_block"]["layout_region_id"] == "page_1:lane_1:region_2"
