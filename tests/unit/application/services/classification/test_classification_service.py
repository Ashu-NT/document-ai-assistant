import pytest

from src.application.services.classification import ClassificationService
from src.application.validation.classification import (
    ChunkClassificationValidator,
    DocumentClassificationValidator,
)
from src.shared.exceptions import SchemaValidationError


class FakeClassificationRepository:
    def __init__(self) -> None:
        self.document_classifications = {}
        self.chunk_classifications = {}

    def save_document_classification(self, classification) -> None:
        self.document_classifications[classification.document_id] = classification

    def get_document_classification(self, document_id: str):
        return self.document_classifications.get(document_id)

    def save_chunk_classification(self, classification) -> None:
        self.chunk_classifications[classification.chunk_id] = classification

    def get_chunk_classification(self, chunk_id: str):
        return self.chunk_classifications.get(chunk_id)

    def list_chunk_classifications(self, document_id: str):
        return [
            classification
            for classification in self.chunk_classifications.values()
            if classification.document_id == document_id
        ]


def make_service(repository: FakeClassificationRepository) -> ClassificationService:
    return ClassificationService(
        repository,
        DocumentClassificationValidator(),
        ChunkClassificationValidator(),
    )


def test_save_document_classification(sample_document_classification) -> None:
    repository = FakeClassificationRepository()
    service = make_service(repository)

    result = service.save_document_classification(sample_document_classification)

    assert result.entity_id == sample_document_classification.document_id
    assert result.payload["document_type"] == "manual"
    assert len(repository.document_classifications) == 1


def test_save_chunk_classification(sample_chunk_classification) -> None:
    repository = FakeClassificationRepository()
    service = make_service(repository)

    result = service.save_chunk_classification(sample_chunk_classification)

    assert result.entity_id == sample_chunk_classification.chunk_id
    assert result.payload["document_id"] == sample_chunk_classification.document_id
    assert len(repository.chunk_classifications) == 1


def test_get_document_classification(sample_document_classification) -> None:
    repository = FakeClassificationRepository()
    repository.save_document_classification(sample_document_classification)

    service = make_service(repository)

    loaded = service.get_document_classification(
        sample_document_classification.document_id
    )

    assert loaded == sample_document_classification


def test_get_chunk_classification(sample_chunk_classification) -> None:
    repository = FakeClassificationRepository()
    repository.save_chunk_classification(sample_chunk_classification)

    service = make_service(repository)

    loaded = service.get_chunk_classification(
        sample_chunk_classification.chunk_id
    )

    assert loaded == sample_chunk_classification


def test_list_chunk_classifications(sample_chunk_classification) -> None:
    repository = FakeClassificationRepository()
    repository.save_chunk_classification(sample_chunk_classification)

    service = make_service(repository)

    results = service.list_chunk_classifications(
        sample_chunk_classification.document_id
    )

    assert len(results) == 1
    assert results[0] == sample_chunk_classification


def test_save_document_classification_rejects_invalid_input(
    sample_document_classification,
) -> None:
    repository = FakeClassificationRepository()
    service = make_service(repository)
    sample_document_classification.result = None

    with pytest.raises(SchemaValidationError):
        service.save_document_classification(sample_document_classification)

    assert repository.document_classifications == {}


def test_save_chunk_classification_rejects_invalid_input(
    sample_chunk_classification,
) -> None:
    repository = FakeClassificationRepository()
    service = make_service(repository)
    sample_chunk_classification.result = None

    with pytest.raises(SchemaValidationError):
        service.save_chunk_classification(sample_chunk_classification)

    assert repository.chunk_classifications == {}
