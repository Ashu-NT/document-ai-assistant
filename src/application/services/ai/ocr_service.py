from src.application.contracts.ai import OCRProvider, OCRResult
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action


class OCRService:
    def __init__(self, ocr_provider: OCRProvider) -> None:
        self.ocr_provider = ocr_provider

    @tracked_action(
        action="ai.ocr.text_extracted",
        activity=True,
        audit=False,
        event=False,
    )
    def extract_text_from_image(
        self,
        image_path: str,
        activity_context: ActivityContext | None = None,
    ) -> str:
        return self.extract_result_from_image(
            image_path,
            activity_context=activity_context,
        ).text

    @tracked_action(
        action="ai.ocr.result_extracted",
        activity=True,
        audit=False,
        event=False,
    )
    def extract_result_from_image(
        self,
        image_path: str,
        activity_context: ActivityContext | None = None,
    ) -> OCRResult:
        raw_result = self.ocr_provider.extract_text_from_image(image_path)
        if isinstance(raw_result, OCRResult):
            if raw_result.source_image_path is None:
                raw_result.source_image_path = image_path
            return raw_result

        return OCRResult(
            text=str(raw_result or "").strip(),
            provider_name=type(self.ocr_provider).__name__,
            source_image_path=image_path,
        )
