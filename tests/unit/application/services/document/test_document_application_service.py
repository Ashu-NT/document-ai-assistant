from src.application.services.document import (
    DocumentApplicationService,
    DocumentLookupService,
    DocumentRegistrationService,
    DuplicateDetectionService,
)


class FakeDocumentRepository:
    pass


def test_document_application_service_groups_document_services() -> None:
    repository = FakeDocumentRepository()

    duplicate_detection = DuplicateDetectionService(repository)
    lookup = DocumentLookupService(repository)
    registration = DocumentRegistrationService(repository)

    service = DocumentApplicationService(
        duplicate_detection=duplicate_detection,
        lookup=lookup,
        registration=registration,
    )

    assert service.duplicate_detection is duplicate_detection
    assert service.lookup is lookup
    assert service.registration is registration