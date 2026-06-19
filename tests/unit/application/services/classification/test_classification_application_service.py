from src.application.services.classification import (
    ClassificationApplicationService,
    ClassificationService,
)
from src.application.validation.classification import (
    ChunkClassificationValidator,
    DocumentClassificationValidator,
)


class FakeClassificationRepository:
    pass


def test_classification_application_service_groups_services() -> None:
    classification_service = ClassificationService(
        FakeClassificationRepository(),
        DocumentClassificationValidator(),
        ChunkClassificationValidator(),
    )

    app_service = ClassificationApplicationService(
        classification=classification_service
    )

    assert app_service.classification is classification_service
