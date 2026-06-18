from src.application.services.extraction import (
    ExtractionApplicationService,
    ExtractionService,
)


class FakeExtractionRepository:
    pass


def test_extraction_application_service_groups_services() -> None:
    extraction_service = ExtractionService(FakeExtractionRepository())

    app_service = ExtractionApplicationService(
        extraction=extraction_service,
    )

    assert app_service.extraction is extraction_service