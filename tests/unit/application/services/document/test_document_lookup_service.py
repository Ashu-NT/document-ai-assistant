from src.application.services.document import DocumentLookupService


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.graphs = {}
        self.chunks = []
        self.identifiers = []

    def get_document_graph(self, document_id: str):
        return self.graphs.get(document_id)

    def get_chunks_by_ids(self, chunk_ids: list[str]):
        return [
            chunk for chunk in self.chunks if chunk.chunk_id in chunk_ids
        ]

    def list_chunks_by_document(self, document_id: str):
        return [
            chunk for chunk in self.chunks if chunk.document_id == document_id
        ]

    def search_identifiers(self, value: str):
        return self.identifiers


def test_get_document_graph(sample_document_graph, document_id) -> None:
    repository = FakeDocumentRepository()
    repository.graphs[document_id] = sample_document_graph

    service = DocumentLookupService(repository)

    graph = service.get_document_graph(document_id)

    assert graph is not None
    assert graph.document.document_id == document_id


def test_get_chunks_by_ids(sample_chunk, chunk_id) -> None:
    repository = FakeDocumentRepository()
    repository.chunks.append(sample_chunk)

    service = DocumentLookupService(repository)

    chunks = service.get_chunks_by_ids([chunk_id])

    assert len(chunks) == 1
    assert chunks[0].chunk_id == chunk_id


def test_list_chunks_by_document(sample_chunk, document_id) -> None:
    repository = FakeDocumentRepository()
    repository.chunks.append(sample_chunk)

    service = DocumentLookupService(repository)

    chunks = service.list_chunks_by_document(document_id)

    assert len(chunks) == 1
    assert chunks[0].document_id == document_id


def test_search_identifiers(sample_identifier) -> None:
    repository = FakeDocumentRepository()
    repository.identifiers.append(sample_identifier)

    service = DocumentLookupService(repository)

    identifiers = service.search_identifiers("HP-001")

    assert len(identifiers) == 1