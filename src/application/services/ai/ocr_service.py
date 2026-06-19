from src.application.contracts.ai import OCRProvider
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
        return self.ocr_provider.extract_text_from_image(image_path)
