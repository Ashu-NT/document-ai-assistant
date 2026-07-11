"""
Tests for DocumentExplorationService.

The service reads exclusively from DocumentGraph — no Qdrant, no embeddings,
no LLM calls. Tests use a FakeDocumentRepository backed by in-memory data;
the absence of any mock/patch for external services proves the service never
reaches them.
"""

import pytest

from src.application.services.document import DocumentLookupService

from src.application.services.document_exploration import (
    DocumentExplorationService,
    DocumentNotFoundError,
)

from src.domain.common import ChunkType

from src.domain.document import Document, DocumentChunk, DocumentGraph, DocumentSection

from src.domain.document.value_objects import DocumentStatistics

class FakeDocumentRepository:
    def __init__(self) -> None:
        self.graphs: dict[str, DocumentGraph] = {}

    def get_document_graph(self, document_id: str) -> DocumentGraph | None:
        return self.graphs.get(document_id)

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list:
        return []

    def list_chunks_by_document(self, document_id: str) -> list:
        return []

    def search_identifiers(self, value: str) -> list:
        return []

@pytest.fixture
def fake_repository() -> FakeDocumentRepository:
    return FakeDocumentRepository()

@pytest.fixture
def lookup_service(fake_repository: FakeDocumentRepository) -> DocumentLookupService:
    return DocumentLookupService(fake_repository)

@pytest.fixture
def service(lookup_service: DocumentLookupService) -> DocumentExplorationService:
    return DocumentExplorationService(lookup_service)

__all__ = [name for name in globals() if not name.startswith("__")]
