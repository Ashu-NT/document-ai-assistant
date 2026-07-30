from src.application.workflows.parsing import ParsedCanonicalElement
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
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
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


def test_marks_page_with_dense_replacement_characters_as_corrupted() -> None:
    analyzer = PageTextQualityAnalyzer(
        OCRSelectionPolicy(min_text_chars_per_page=10, min_replacement_char_ratio=0.03)
    )
    # A subset font missing ToUnicode entries for accented characters --
    # every umlaut in this real-world-shaped sentence decoded to U+FFFD.
    elements = [
        make_element(
            element_id="txt_1",
            element_type=ElementType.TEXT,
            text="L�rssen-Kr�ger Werft GmbH & Co. KG, Bremen",
            page_number=1,
            bbox=BoundingBox(0.0, 0.0, 1.0, 1.0),
        )
    ]

    result = analyzer.analyze(elements, page_count=1)

    assert result[0].replacement_char_count == 2
    assert result[0].has_corrupted_text is True
    assert "corrupted_text_detected" in result[0].reasons


def test_does_not_flag_page_with_a_single_incidental_replacement_character() -> None:
    analyzer = PageTextQualityAnalyzer(
        OCRSelectionPolicy(min_text_chars_per_page=10, min_replacement_char_ratio=0.05)
    )
    elements = [
        make_element(
            element_id="txt_1",
            element_type=ElementType.TEXT,
            text=(
                "This is a long, otherwise perfectly clean page of extracted "
                "text with just one stray � character in it, well below "
                "the significance threshold for flagging real corruption."
            ),
            page_number=1,
            bbox=BoundingBox(0.0, 0.0, 1.0, 1.0),
        )
    ]

    result = analyzer.analyze(elements, page_count=1)

    assert result[0].replacement_char_count == 1
    assert result[0].has_corrupted_text is False
    assert "corrupted_text_detected" not in result[0].reasons

