from dataclasses import replace

from src.domain.common import BoundingBox
from src.domain.retrieval import RowBoundingBox


def test_citation_display_text(sample_citation) -> None:
    text = sample_citation.display_text()

    assert "pump_manual.pdf" in text
    assert "Maintenance Schedule" in text
    assert "page: 10" in text


def test_citation_row_bboxes_default_to_none(sample_citation) -> None:
    assert sample_citation.row_bboxes is None


def test_citation_can_carry_row_bboxes(sample_citation) -> None:
    row_bbox = RowBoundingBox(
        row_index=2,
        page_number=10,
        bbox=BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0),
    )

    citation_with_rows = replace(sample_citation, row_bboxes=[row_bbox])

    assert citation_with_rows.row_bboxes == [row_bbox]
    assert citation_with_rows.row_bboxes[0].bbox.x2 == 3.0