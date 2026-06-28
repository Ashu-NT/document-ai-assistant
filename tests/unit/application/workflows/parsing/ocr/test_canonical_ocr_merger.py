from src.application.contracts.ai import OCRResult
from src.application.workflows.parsing import CanonicalElement
from src.application.workflows.parsing.ocr import (
    CanonicalOCRMerger,
    OCRMergePolicy,
    OCRSelectionResult,
    OCRTarget,
    OCRTargetExecutionResult,
    OCRTargetType,
)
from src.domain.common import BoundingBox, ElementType
from src.shared.ids import IdGenerator


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


def test_creates_synthetic_page_ocr_element() -> None:
    merger = CanonicalOCRMerger(
        id_generator=IdGenerator(),
        merge_policy=OCRMergePolicy(),
    )
    elements = [
        make_element(
            element_id="hdr_1",
            element_type=ElementType.SECTION_HEADER,
            text="Maintenance",
            page_number=1,
        )
    ]
    target = OCRTarget(
        target_id="page:1",
        target_type=OCRTargetType.PAGE,
        document_path="manual.pdf",
        page_number=1,
        reason="probable_scanned_page",
    )
    execution = OCRTargetExecutionResult(
        target=target,
        source_image_path="page_1.png",
        ocr_result=OCRResult(
            text="Torque setting 35 Nm",
            provider_name="FakeOCR",
            confidence=0.9,
        ),
    )

    result = merger.merge(
        document_path="manual.pdf",
        page_count=1,
        canonical_elements=elements,
        selection_result=OCRSelectionResult(targets=[target]),
        execution_results=[execution],
    )

    assert result.added_synthetic_elements == 1
    assert any(
        element.metadata.get("ocr_target_type") == "page"
        for element in result.canonical_elements
    )


def test_attaches_asset_ocr_metadata_without_creating_duplicate_page_text() -> None:
    merger = CanonicalOCRMerger(
        id_generator=IdGenerator(),
        merge_policy=OCRMergePolicy(),
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
    target = OCRTarget(
        target_id="asset:pic_1",
        target_type=OCRTargetType.ASSET,
        document_path="manual.pdf",
        page_number=1,
        image_path="outputs/images/pic_1.png",
        source_element_id="pic_1",
        reason="asset_image_without_ocr",
    )
    execution = OCRTargetExecutionResult(
        target=target,
        source_image_path="outputs/images/pic_1.png",
        ocr_result=OCRResult(
            text="FILTER HOUSING",
            provider_name="FakeOCR",
            confidence=0.92,
        ),
    )

    result = merger.merge(
        document_path="manual.pdf",
        page_count=1,
        canonical_elements=elements,
        selection_result=OCRSelectionResult(targets=[target]),
        execution_results=[execution],
    )

    assert result.updated_asset_elements == 1
    assert result.added_synthetic_elements == 0
    assert result.canonical_elements[0].metadata["ocr_text"] == "FILTER HOUSING"

