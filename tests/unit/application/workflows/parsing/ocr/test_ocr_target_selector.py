from src.application.workflows.parsing import CanonicalElement
from src.application.workflows.parsing.ocr import (
    OCRSelectionPolicy,
    OCRTargetSelector,
    OCRTargetType,
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


def test_selects_asset_target_for_image_without_ocr() -> None:
    policy = OCRSelectionPolicy(asset_enabled=True)
    selector = OCRTargetSelector(
        page_text_quality_analyzer=PageTextQualityAnalyzer(policy),
        policy=policy,
    )
    elements = [
        make_element(
            element_id="pic_1",
            element_type=ElementType.PICTURE,
            text=None,
            page_number=1,
            metadata={"image_path": "outputs/images/pic_1.png"},
        )
    ]

    result = selector.select(
        document_path="manual.pdf",
        canonical_elements=elements,
        page_count=1,
    )

    assert len(result.targets) == 1
    assert result.targets[0].target_type == OCRTargetType.ASSET
    assert result.targets[0].image_path == "outputs/images/pic_1.png"


def test_selects_page_target_only_for_text_poor_pages_and_respects_limit() -> None:
    policy = OCRSelectionPolicy(
        asset_enabled=False,
        page_fallback_enabled=True,
        max_pages_per_document=1,
        min_text_chars_per_page=60,
    )
    selector = OCRTargetSelector(
        page_text_quality_analyzer=PageTextQualityAnalyzer(policy),
        policy=policy,
    )
    elements = [
        make_element(
            element_id="pic_1",
            element_type=ElementType.PICTURE,
            text=None,
            page_number=1,
            bbox=BoundingBox(0.0, 0.0, 1.0, 1.0),
            metadata={"image_path": "page_1.png"},
        ),
        make_element(
            element_id="pic_2",
            element_type=ElementType.PICTURE,
            text=None,
            page_number=2,
            bbox=BoundingBox(0.0, 0.0, 1.0, 1.0),
            metadata={"image_path": "page_2.png"},
        ),
    ]

    result = selector.select(
        document_path="manual.pdf",
        canonical_elements=elements,
        page_count=2,
    )

    page_targets = [
        target for target in result.targets if target.target_type == OCRTargetType.PAGE
    ]
    assert len(page_targets) == 1
    assert result.warnings == ["Reached OCR page fallback limit for this document."]

