from __future__ import annotations

from src.application.contracts.document import DocumentCatalogEntry, DocumentRepository


class DocumentCatalogService:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository

    def list_documents(self) -> list[DocumentCatalogEntry]:
        return self.document_repository.list_document_entries()

    def find_documents(self, query_text: str) -> list[DocumentCatalogEntry]:
        return self.document_repository.find_document_entries(query_text)

    def get_document(self, document_id: str) -> DocumentCatalogEntry | None:
        return self.document_repository.get_document_entry(document_id)

    def get_latest_document(self) -> DocumentCatalogEntry | None:
        return self.document_repository.get_latest_document_entry()
