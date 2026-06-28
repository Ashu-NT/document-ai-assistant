from src.application.workflows.parsing import CanonicalElement
from src.application.workflows.parsing.ocr import (
    OCRSelectionPolicy,
    PageTextQualityAnalyzer,
)
from src.domain.common import BoundingBox, ElementType


def make_element(
    *,
    element_id: str,
    element_type: ElementType,
    text: str | None,
    page_number: int,
    bbox: BoundingBox | None = None,
    metadata: dict | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        page_start=page_number,
        page_end=page_number,
        bbox=bbox,
        order_index=1,
        metadata=metadata or {},
    )


def test_marks_page_with_enough_text_as_not_text_poor() -> None:
    analyzer = PageTextQualityAnalyzer(
        OCRSelectionPolicy(min_text_chars_per_page=40)
    )
    elements = [
        make_element(
            element_id="txt_1",
            element_type=ElementType.TEXT,
            text="This page contains enough extracted text for the parser to skip OCR.",
            page_number=1,
            bbox=BoundingBox(0.0, 0.0, 1.0, 1.0),
        )
    ]

    result = analyzer.analyze(elements, page_count=1)

    assert len(result) == 1
    assert result[0].is_text_poor is False
    assert result[0].has_text is True


def test_marks_empty_image_heavy_page_as_text_poor() -> None:
    analyzer = PageTextQualityAnalyzer(
        OCRSelectionPolicy(
            min_text_chars_per_page=80,
            min_image_area_ratio=0.3,
        )
    )
    elements = [
        make_element(
            element_id="pic_1",
            element_type=ElementType.PICTURE,
            text=None,
            page_number=1,
            bbox=BoundingBox(0.0, 0.0, 1.0, 1.0),
            metadata={"image_path": "page_1.png"},
        )
    ]

    result = analyzer.analyze(elements, page_count=1)

    assert result[0].is_text_poor is True
    assert result[0].is_probably_scanned is True
    assert "no_extracted_text" in result[0].reasons

