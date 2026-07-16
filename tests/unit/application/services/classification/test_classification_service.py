import pytest

from src.application.services.classification import ClassificationService
from src.application.validation.classification import DocumentClassificationValidator
from src.shared.exceptions import SchemaValidationError


class FakeClassificationRepository:
    def __init__(self) -> None:
        self.document_classifications = {}

    def save_document_classification(self, classification) -> None:
        self.document_classifications[classification.document_id] = classification

    def get_document_classification(self, document_id: str):
        return self.document_classifications.get(document_id)


def make_service(repository: FakeClassificationRepository) -> ClassificationService:
    return ClassificationService(
        repository,
        DocumentClassificationValidator(),
    )


def test_save_document_classification(sample_document_classification) -> None:
    repository = FakeClassificationRepository()
    service = make_service(repository)

    result = service.save_document_classification(sample_document_classification)

    assert result.entity_id == sample_document_classification.document_id
    assert result.payload["document_type"] == "manual"
    assert len(repository.document_classifications) == 1


def test_get_document_classification(sample_document_classification) -> None:
    repository = FakeClassificationRepository()
    repository.save_document_classification(sample_document_classification)

    service = make_service(repository)

    loaded = service.get_document_classification(
        sample_document_classification.document_id
    )

    assert loaded == sample_document_classification


def test_save_document_classification_rejects_invalid_input(
    sample_document_classification,
) -> None:
    repository = FakeClassificationRepository()
    service = make_service(repository)
    sample_document_classification.result = None

    with pytest.raises(SchemaValidationError):
        service.save_document_classification(sample_document_classification)

    assert repository.document_classifications == {}
