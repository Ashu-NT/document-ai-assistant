from src.domain.common import BoundingBox, SourceLocation
from src.infrastructure.db.mappers import (
    bbox_to_columns,
    columns_to_source_location,
)


def test_bbox_to_columns_with_bbox() -> None:
    source = SourceLocation(
        page_start=1,
        page_end=2,
        bbox=BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0),
    )

    columns = bbox_to_columns(source)

    assert columns["page_start"] == 1
    assert columns["page_end"] == 2
    assert columns["bbox_x1"] == 1.0
    assert columns["bbox_y1"] == 2.0
    assert columns["bbox_x2"] == 3.0
    assert columns["bbox_y2"] == 4.0


def test_columns_to_source_location_without_bbox() -> None:
    source = columns_to_source_location(
        page_start=5,
        page_end=6,
    )

    assert source.page_start == 5
    assert source.page_end == 6
    assert source.bbox is None


def test_columns_to_source_location_with_bbox() -> None:
    source = columns_to_source_location(
        page_start=1,
        page_end=1,
        bbox_x1=1.0,
        bbox_y1=2.0,
        bbox_x2=3.0,
        bbox_y2=4.0,
    )

    assert source.bbox is not None
    assert source.bbox.x1 == 1.0