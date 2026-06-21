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
            ocr_text = self.ocr_service.extract_text_from_image(
                image_path,
                activity_context=activity_context,
            )
        except OCRProviderError as exc:
            # OCR enrichment is optional; keep parsing moving and retain diagnostics.
            metadata["ocr_error"] = exc.message
            return

        clean_ocr_text = self._clean_text(ocr_text)
        if clean_ocr_text is not None:
            metadata["ocr_text"] = clean_ocr_text

    @staticmethod
    def _clean_text(value: object) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        return text or None
