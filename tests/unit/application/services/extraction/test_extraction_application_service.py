from src.application.services.extraction import (
    ExtractionApplicationService,
    ExtractionService,
)
from src.application.validation.extraction import ExtractionResultValidator


class FakeExtractionRepository:
    pass


def test_extraction_application_service_groups_services() -> None:
    extraction_service = ExtractionService(
        FakeExtractionRepository(),
        ExtractionResultValidator(),
    )

    app_service = ExtractionApplicationService(
        extraction=extraction_service,
    )

    assert app_service.extraction is extraction_service
