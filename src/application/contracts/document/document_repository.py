from typing import Protocol

from src.domain.document import DocumentGraph
from src.domain.document.entities import DocumentChunk, Identifier
from src.application.contracts.document.document_catalog_entry import DocumentCatalogEntry


class DocumentRepository(Protocol):
    def find_document_id_by_file_hash(self, file_hash: str) -> str | None:
        ...

    def find_document_id_by_content_hash(self, content_hash: str) -> str | None:
        ...

    def save_document_graph(self, document_graph: DocumentGraph) -> None:
        ...

    def replace_document_graph(self, document_graph: DocumentGraph) -> None:
        ...

    def replace_document_chunk_artifacts(self, document_graph: DocumentGraph) -> None:
        ...

    def get_document_graph(self, document_id: str) -> DocumentGraph | None:
        ...

    def list_document_entries(self) -> list[DocumentCatalogEntry]:
        ...

    def find_document_entries(self, query_text: str) -> list[DocumentCatalogEntry]:
        ...

    def get_document_entry(self, document_id: str) -> DocumentCatalogEntry | None:
        ...

    def get_latest_document_entry(self) -> DocumentCatalogEntry | None:
        ...

    def list_chunks_by_document(self, document_id: str) -> list[DocumentChunk]:
        ...

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[DocumentChunk]:
        ...

    def search_identifiers(self, value: str) -> list[Identifier]:
        ...

    def search_identifiers_by_type(self, identifier_type: str, document_id: str) -> list[Identifier]:
        ...

    def get_identifiers_for_chunk(self, chunk_id: str) -> list[Identifier]:
        ...

    def write_document_identifiers(self, identifiers: list[Identifier]) -> None:
        ...
