from src.application.workflows.parsing import CanonicalElement as ParsedCanonicalElement
from src.application.workflows.parsing.canonical_element_ocr_enricher import (
    CanonicalElementOCREnricher,
)
from src.domain.common import ElementType
from src.shared.exceptions import OCRProviderError


class FakeOCRService:
    def __init__(self, result: str = "Detected OCR text") -> None:
        self.result = result
        self.calls: list[str] = []

    def extract_text_from_image(
        self,
        image_path: str,
        activity_context=None,
    ) -> str:
        self.calls.append(image_path)
        return self.result


class FailingOCRService:
    def extract_text_from_image(
        self,
        image_path: str,
        activity_context=None,
    ) -> str:
        raise OCRProviderError(
            "OCR provider failed.",
            details={"image_path": image_path},
        )


def make_picture_element(*, metadata: dict | None = None) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id="pic_001",
        document_id="doc_001",
        element_type=ElementType.PICTURE,
        order_index=1,
        metadata=metadata or {},
    )


def test_enrich_adds_ocr_text_for_image_elements() -> None:
    element = make_picture_element(
        metadata={"image_path": "outputs/images/pic_001.png"},
    )
    ocr_service = FakeOCRService("FILTER HOUSING HP-001")
    enricher = CanonicalElementOCREnricher(ocr_service)

    result = enricher.enrich([element])

    assert result[0].metadata["ocr_text"] == "FILTER HOUSING HP-001"
    assert ocr_service.calls == ["outputs/images/pic_001.png"]


def test_enrich_skips_elements_without_image_path() -> None:
    element = make_picture_element(metadata={})
    ocr_service = FakeOCRService()
    enricher = CanonicalElementOCREnricher(ocr_service)

    enricher.enrich([element])

    assert "ocr_text" not in element.metadata
    assert ocr_service.calls == []


def test_enrich_preserves_existing_ocr_text() -> None:
    element = make_picture_element(
        metadata={
            "image_path": "outputs/images/pic_001.png",
            "ocr_text": "Existing OCR text",
        }
    )
    ocr_service = FakeOCRService()
    enricher = CanonicalElementOCREnricher(ocr_service)

    enricher.enrich([element])

    assert element.metadata["ocr_text"] == "Existing OCR text"
    assert ocr_service.calls == []


def test_enrich_keeps_parsing_moving_when_ocr_fails() -> None:
    element = make_picture_element(
        metadata={"image_path": "outputs/images/pic_001.png"},
    )
    enricher = CanonicalElementOCREnricher(FailingOCRService())

    result = enricher.enrich([element])

    assert result[0].metadata["ocr_error"] == "OCR provider failed."
    assert "ocr_text" not in result[0].metadata
