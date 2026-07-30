import time

from src.application.contracts.ai import OCRProvider, OCRResult
from src.shared.activity import ActivityContext
from src.shared.exceptions import OCRProviderError
from src.shared.execution import tracked_action


class OCRService:
    def __init__(
        self,
        ocr_provider: OCRProvider,
        *,
        retry_attempts: int = 0,
        retry_backoff_seconds: float = 0.0,
    ) -> None:
        self.ocr_provider = ocr_provider
        self.retry_attempts = retry_attempts
        self.retry_backoff_seconds = retry_backoff_seconds

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
        raw_result = self._extract_with_retry(image_path)
        if isinstance(raw_result, OCRResult):
            if raw_result.source_image_path is None:
                raw_result.source_image_path = image_path
            return raw_result

        return OCRResult(
            text=str(raw_result or "").strip(),
            provider_name=type(self.ocr_provider).__name__,
            source_image_path=image_path,
        )

    def _extract_with_retry(self, image_path: str) -> OCRResult | str:
        last_error: OCRProviderError | None = None
        for attempt in range(1 + self.retry_attempts):
            try:
                return self.ocr_provider.extract_text_from_image(image_path)
            except OCRProviderError as exc:
                last_error = exc
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_backoff_seconds * (attempt + 1))
        assert last_error is not None  # loop always runs >= 1 iteration
        raise last_error
