from enum import Enum

from src.application.workflows.parsing.normalizers.provenance.docling_bbox_normalizer import (
    DoclingBBoxNormalizer,
)


class _Origin(Enum):
    TOPLEFT = "top-left"
    BOTTOMLEFT = "bottom-left"


def test_converts_top_left_bbox_to_bottom_left_coordinates() -> None:
    bbox = DoclingBBoxNormalizer.normalize(
        {
            "l": 10,
            "t": 20,
            "r": 110,
            "b": 50,
            "coord_origin": "TOPLEFT",
        },
        page_height=200,
    )

    assert bbox is not None
    assert (bbox.x1, bbox.y1, bbox.x2, bbox.y2) == (10, 180, 110, 150)


def test_normalizes_bottom_left_bbox_order_without_flipping_page_axis() -> None:
    bbox = DoclingBBoxNormalizer.normalize(
        {
            "l": 110,
            "t": 50,
            "r": 10,
            "b": 20,
            "coord_origin": _Origin.BOTTOMLEFT,
        },
        page_height=200,
    )

    assert bbox is not None
    assert (bbox.x1, bbox.y1, bbox.x2, bbox.y2) == (10, 50, 110, 20)


def test_explicit_top_left_origin_requires_page_height() -> None:
    bbox = DoclingBBoxNormalizer.normalize(
        {"l": 10, "t": 20, "r": 110, "b": 50, "coord_origin": "TOPLEFT"},
        page_height=None,
    )

    assert bbox is None


def test_unknown_explicit_origin_is_not_silently_assumed() -> None:
    bbox = DoclingBBoxNormalizer.normalize(
        {"l": 10, "t": 20, "r": 110, "b": 50, "coord_origin": "CENTER"},
        page_height=200,
    )

    assert bbox is None


def test_originless_legacy_bbox_preserves_existing_coordinate_order() -> None:
    bbox = DoclingBBoxNormalizer.normalize(
        {"x1": 10, "y1": 20, "x2": 110, "y2": 50},
        page_height=None,
    )

    assert bbox is not None
    assert (bbox.x1, bbox.y1, bbox.x2, bbox.y2) == (10, 20, 110, 50)
