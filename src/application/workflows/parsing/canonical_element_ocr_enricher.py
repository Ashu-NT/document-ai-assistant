from src.application.contracts.ai import OCRResult
from src.application.services.ai import OCRService
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.shared.activity import ActivityContext
from src.shared.exceptions import OCRProviderError


class CanonicalElementOCREnricher:
    def __init__(self, ocr_service: OCRService) -> None:
        self.ocr_service = ocr_service

    def enrich(
        self,
        canonical_elements: list[CanonicalElement],
        *,
        activity_context: ActivityContext | None = None,
    ) -> list[CanonicalElement]:
        for element in canonical_elements:
            self._enrich_element(
                element,
                activity_context=activity_context,
            )

        return canonical_elements

    def _enrich_element(
        self,
        element: CanonicalElement,
        *,
        activity_context: ActivityContext | None = None,
    ) -> None:
        metadata = element.metadata
        image_path = self._clean_text(metadata.get("image_path"))

        if image_path is None or self._clean_text(metadata.get("ocr_text")) is not None:
            return

        try:
            ocr_result = self._extract_result(
                image_path,
                activity_context=activity_context,
            )
        except OCRProviderError as exc:
            # OCR enrichment is optional; keep parsing moving and retain diagnostics.
            metadata["ocr_error"] = exc.message
            return

        clean_ocr_text = self._clean_text(ocr_result.text)
        if clean_ocr_text is not None:
            metadata["ocr_text"] = clean_ocr_text
            metadata["ocr_provider"] = ocr_result.provider_name
            if ocr_result.confidence is not None:
                metadata["ocr_confidence"] = ocr_result.confidence

    def _extract_result(
        self,
        image_path: str,
        *,
        activity_context: ActivityContext | None = None,
    ) -> OCRResult:
        extract_result = getattr(self.ocr_service, "extract_result_from_image", None)
        if callable(extract_result):
            return extract_result(
                image_path,
                activity_context=activity_context,
            )

        extract_text = getattr(self.ocr_service, "extract_text_from_image")
        return OCRResult(
            text=extract_text(
                image_path,
                activity_context=activity_context,
            ),
            provider_name=type(self.ocr_service).__name__,
            source_image_path=image_path,
        )

    @staticmethod
    def _clean_text(value: object) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        return text or None
