from typing import Protocol

from src.domain.document import DocumentGraph
from src.domain.document.entities import DocumentChunk, Identifier


class DocumentRepository(Protocol):
    def find_document_id_by_file_hash(self, file_hash: str) -> str | None:
        ...

    def find_document_id_by_content_hash(self, content_hash: str) -> str | None:
        ...

    def save_document_graph(self, document_graph: DocumentGraph) -> None:
        ...

    def replace_document_chunk_artifacts(self, document_graph: DocumentGraph) -> None:
        ...

    def get_document_graph(self, document_id: str) -> DocumentGraph | None:
        ...

    def list_chunks_by_document(self, document_id: str) -> list[DocumentChunk]:
        ...

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[DocumentChunk]:
        ...

    def search_identifiers(self, value: str) -> list[Identifier]:
        ...
