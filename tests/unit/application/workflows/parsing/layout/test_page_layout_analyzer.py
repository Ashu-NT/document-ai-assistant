from types import SimpleNamespace

from src.application.workflows.parsing.layout.page_layout_analyzer import (
    PageLayoutAnalyzer,
)
from src.application.workflows.parsing.layout.models.layout_region_role import (
    LayoutRegionRole,
)
from src.application.workflows.parsing.layout.models.page_layout_candidate import (
    PageLayoutCandidate,
)
from src.domain.common import BoundingBox


def _raw_document_with_page_size(
    *,
    width: float,
    height: float,
) -> SimpleNamespace:
    return SimpleNamespace(
        pages={
            1: SimpleNamespace(size=SimpleNamespace(width=width, height=height)),
            2: SimpleNamespace(size=SimpleNamespace(width=width, height=height)),
        }
    )


def test_page_layout_analyzer_detects_parallel_lanes_and_serializes_metadata() -> None:
    analyzer = PageLayoutAnalyzer()
    raw_document = _raw_document_with_page_size(width=1000, height=1400)
    candidates = [
        PageLayoutCandidate(
            element_ref="left_1",
            page_number=1,
            bbox=BoundingBox(x1=60, y1=100, x2=430, y2=180),
            label="text",
            text="Left column introduction",
        ),
        PageLayoutCandidate(
            element_ref="left_2",
            page_number=1,
            bbox=BoundingBox(x1=70, y1=220, x2=420, y2=300),
            label="text",
            text="Left column procedure",
        ),
        PageLayoutCandidate(
            element_ref="right_1",
            page_number=1,
            bbox=BoundingBox(x1=580, y1=110, x2=930, y2=190),
            label="text",
            text="Right column notes",
        ),
        PageLayoutCandidate(
            element_ref="right_2",
            page_number=1,
            bbox=BoundingBox(x1=590, y1=230, x2=940, y2=310),
            label="text",
            text="Right column details",
        ),
    ]

    metadata = analyzer.analyze_and_serialize(
        raw_document=raw_document,
        candidates=candidates,
    )

    assert metadata["left_1"]["page_orientation"] == "portrait"
    assert metadata["left_1"]["layout_lane_count"] == 2
    assert metadata["left_1"]["layout_lane_index"] == 1
    assert metadata["left_1"]["layout_region_id"] == "page_1:lane_1"
    assert metadata["left_1"]["layout_region_role"] == LayoutRegionRole.PARALLEL_COLUMN
    assert metadata["right_1"]["layout_lane_index"] == 2
    assert metadata["right_1"]["layout_region_id"] == "page_1:lane_2"


def test_page_layout_analyzer_marks_pre_body_pages_as_front_matter() -> None:
    analyzer = PageLayoutAnalyzer()
    raw_document = _raw_document_with_page_size(width=1000, height=1400)
    candidates = [
        PageLayoutCandidate(
            element_ref="toc_title",
            page_number=1,
            bbox=BoundingBox(x1=100, y1=80, x2=500, y2=130),
            label="title",
            text="Table of Contents",
        ),
        PageLayoutCandidate(
            element_ref="toc_entry",
            page_number=1,
            bbox=BoundingBox(x1=120, y1=170, x2=520, y2=210),
            label="text",
            text="1 Introduction 5",
        ),
        PageLayoutCandidate(
            element_ref="body_header",
            page_number=2,
            bbox=BoundingBox(x1=90, y1=90, x2=600, y2=130),
            label="section_header",
            text="1 Introduction",
        ),
        PageLayoutCandidate(
            element_ref="body_text_1",
            page_number=2,
            bbox=BoundingBox(x1=90, y1=170, x2=900, y2=260),
            label="text",
            text="This page begins the operating instructions for the system.",
        ),
        PageLayoutCandidate(
            element_ref="body_text_2",
            page_number=2,
            bbox=BoundingBox(x1=90, y1=280, x2=900, y2=360),
            label="text",
            text="It contains enough narrative body content to count as the main document body.",
        ),
        PageLayoutCandidate(
            element_ref="body_text_3",
            page_number=2,
            bbox=BoundingBox(x1=90, y1=380, x2=900, y2=460),
            label="text",
            text="Additional content keeps the detection generic and independent of any sample document.",
        ),
    ]

    metadata = analyzer.analyze_and_serialize(
        raw_document=raw_document,
        candidates=candidates,
    )

    assert metadata["toc_title"]["layout_is_front_matter"] is True
    assert metadata["toc_entry"]["layout_region_role"] == LayoutRegionRole.FRONT_MATTER
    assert "layout_is_front_matter" not in metadata["body_header"]
