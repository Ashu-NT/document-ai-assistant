from src.application.services.extraction.extraction_service import ExtractionService


class ExtractionApplicationService:
    def __init__(self, extraction: ExtractionService) -> None:
        self.extraction = extraction