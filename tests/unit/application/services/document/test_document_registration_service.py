import pytest

from src.application.services.document import DocumentRegistrationService
from src.application.validation.document import DocumentGraphValidator
from src.shared.exceptions import SchemaValidationError


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.saved_graphs = []
        self.replaced_full_graphs = []
        self.replaced_graphs = []

    def save_document_graph(self, document_graph) -> None:
        self.saved_graphs.append(document_graph)

    def replace_document_graph(self, document_graph) -> None:
        self.replaced_full_graphs.append(document_graph)

    def replace_document_chunk_artifacts(self, document_graph) -> None:
        self.replaced_graphs.append(document_graph)


def make_service(repository: FakeDocumentRepository) -> DocumentRegistrationService:
    return DocumentRegistrationService(
        repository,
        DocumentGraphValidator(),
    )


def test_register_document_graph(sample_document_graph, document_id) -> None:
    repository = FakeDocumentRepository()
    service = make_service(repository)

    result = service.register_document_graph(sample_document_graph)

    assert len(repository.saved_graphs) == 1
    assert result.entity_id == document_id
    assert result.payload["document_id"] == document_id
    assert result.payload["chunk_count"] == 1


def test_register_document_graph_rejects_invalid_input(
    sample_document_graph,
) -> None:
    repository = FakeDocumentRepository()
    service = make_service(repository)
    chunk = next(iter(sample_document_graph.chunks.values()))
    chunk.document_id = "doc_other"

    with pytest.raises(SchemaValidationError):
        service.register_document_graph(sample_document_graph)

    assert repository.saved_graphs == []


def test_replace_document_chunk_artifacts(sample_document_graph, document_id) -> None:
    repository = FakeDocumentRepository()
    service = make_service(repository)

    result = service.replace_document_chunk_artifacts(sample_document_graph)

    assert len(repository.replaced_graphs) == 1
    assert result.entity_id == document_id
    assert result.payload["document_id"] == document_id
    assert result.payload["question_count"] == 1


def test_replace_document_graph(sample_document_graph, document_id) -> None:
    repository = FakeDocumentRepository()
    service = make_service(repository)

    result = service.replace_document_graph(sample_document_graph)

    assert len(repository.replaced_full_graphs) == 1
    assert result.entity_id == document_id
    assert result.payload["document_id"] == document_id
    assert result.payload["chunk_count"] == 1
