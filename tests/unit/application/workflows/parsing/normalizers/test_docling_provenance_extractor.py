from types import SimpleNamespace

from src.application.workflows.parsing.normalizers.provenance.docling_provenance_extractor import (
    DoclingProvenanceExtractor,
)


def test_normalizes_provenance_bbox_using_its_page_height() -> None:
    item = {
        "prov": [
            {
                "page_no": 2,
                "bbox": {
                    "l": 10,
                    "t": 20,
                    "r": 110,
                    "b": 50,
                    "coord_origin": "TOPLEFT",
                },
            }
        ]
    }
    raw_document = SimpleNamespace(
        pages={2: SimpleNamespace(size=SimpleNamespace(height=200))}
    )

    bbox = DoclingProvenanceExtractor().extract_bbox(
        item,
        raw_document=raw_document,
    )

    assert bbox is not None
    assert (bbox.x1, bbox.y1, bbox.x2, bbox.y2) == (10, 180, 110, 150)


def test_uses_parent_page_for_bbox_without_cell_provenance() -> None:
    cell = {
        "bbox": {
            "l": 5,
            "t": 25,
            "r": 50,
            "b": 45,
            "coord_origin": "TOPLEFT",
        }
    }
    raw_document = {"pages": {4: {"size": {"height": 300}}}}

    bbox = DoclingProvenanceExtractor().extract_bbox(
        cell,
        raw_document=raw_document,
        default_page_number=4,
    )

    assert bbox is not None
    assert (bbox.x1, bbox.y1, bbox.x2, bbox.y2) == (5, 275, 50, 255)
