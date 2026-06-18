from src.application.services.document import DocumentRegistrationService


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.saved_graphs = []

    def save_document_graph(self, document_graph) -> None:
        self.saved_graphs.append(document_graph)


def test_register_document_graph(sample_document_graph, document_id) -> None:
    repository = FakeDocumentRepository()
    service = DocumentRegistrationService(repository)

    result = service.register_document_graph(sample_document_graph)

    assert len(repository.saved_graphs) == 1
    assert result.entity_id == document_id
    assert result.payload["document_id"] == document_id
    assert result.payload["chunk_count"] == 1