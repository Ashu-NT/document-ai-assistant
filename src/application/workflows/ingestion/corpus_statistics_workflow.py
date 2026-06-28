from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Protocol

from src.application.services.document import (
    DocumentCatalogService,
    DocumentLookupService,
)
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action


class _VectorMappingReader(Protocol):
    def list_chunk_ids_by_document(self, document_id: str) -> list[str]:
        ...


@dataclass(slots=True)
class CorpusStatisticsResult:
    document_count: int
    page_count: int
    section_count: int
    chunk_count: int
    vector_count: int | None
    documents_by_type: dict[str, int]
    chunks_by_type: dict[str, int]
    identifiers_by_type: dict[str, int]
    failed_ingestion_count: int | None
    diagnostics: dict[str, Any] = field(default_factory=dict)


class CorpusStatisticsWorkflow:
    def __init__(
        self,
        *,
        document_catalog_service: DocumentCatalogService,
        document_lookup_service: DocumentLookupService | None = None,
        vector_mapping_repository: _VectorMappingReader | None = None,
    ) -> None:
        self.document_catalog_service = document_catalog_service
        self.document_lookup_service = document_lookup_service
        self.vector_mapping_repository = vector_mapping_repository

    @tracked_action(
        action="document.corpus_statistics.generated",
        entity_type="document",
        activity=True,
        audit=False,
        event=False,
    )
    def run(
        self,
        activity_context: ActivityContext | None = None,
    ) -> CorpusStatisticsResult:
        documents = self.document_catalog_service.list_documents()
        documents_by_type = Counter(entry.document_type for entry in documents)
        chunks_by_type: Counter[str] = Counter()
        identifiers_by_type: Counter[str] = Counter()
        vector_count: int | None = 0 if self.vector_mapping_repository is not None else None
        graphs_loaded = 0

        if self.document_lookup_service is not None:
            for entry in documents:
                graph = self.document_lookup_service.get_document_graph(
                    entry.document_id,
                    activity_context=activity_context,
                )
                if graph is None:
                    continue
                graphs_loaded += 1
                chunks_by_type.update(
                    chunk.chunk_type.value
                    for chunk in graph.chunks.values()
                )
                identifiers_by_type.update(
                    identifier.identifier_type.value
                    for identifier in graph.identifiers.values()
                )
                if self.vector_mapping_repository is not None and vector_count is not None:
                    vector_count += len(
                        self.vector_mapping_repository.list_chunk_ids_by_document(
                            entry.document_id
                        )
                    )

        return CorpusStatisticsResult(
            document_count=len(documents),
            page_count=sum(entry.page_count or 0 for entry in documents),
            section_count=sum(entry.section_count for entry in documents),
            chunk_count=sum(entry.chunk_count for entry in documents),
            vector_count=vector_count,
            documents_by_type=dict(documents_by_type),
            chunks_by_type=dict(chunks_by_type),
            identifiers_by_type=dict(identifiers_by_type),
            failed_ingestion_count=None,
            diagnostics={
                "documents_loaded": len(documents),
                "graphs_loaded": graphs_loaded,
            },
        )
