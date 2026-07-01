from src.application.contracts.document import DocumentRepository
from src.domain.document import DocumentGraph
from src.domain.document.entities import DocumentChunk, Identifier
from src.shared.activity import ActivityContext
from src.shared.execution import ActionResult, tracked_action


class DocumentLookupService:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository

    @tracked_action(
        action="document.graph_loaded",
        entity_type="document",
        activity=True,
        audit=False,
        event=False,
    )
    def get_document_graph(
        self,
        document_id: str,
        activity_context: ActivityContext | None = None,
    ) -> DocumentGraph | None:
        return self.document_repository.get_document_graph(document_id)

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[DocumentChunk]:
        return self.document_repository.get_chunks_by_ids(chunk_ids)

    def list_chunks_by_document(self, document_id: str) -> list[DocumentChunk]:
        return self.document_repository.list_chunks_by_document(document_id)

    def search_identifiers(self, value: str) -> list[Identifier]:
        return self.document_repository.search_identifiers(value)

    def search_identifiers_by_type(self, identifier_type: str, document_id: str) -> list[Identifier]:
        return self.document_repository.search_identifiers_by_type(identifier_type, document_id)

    def get_identifiers_for_chunk(self, chunk_id: str) -> list[Identifier]:
        return self.document_repository.get_identifiers_for_chunk(chunk_id)