from __future__ import annotations

from src.application.contracts.document import DocumentCatalogEntry
from src.application.workflows.ingestion import CorpusStatisticsWorkflow


class FakeDocumentCatalogService:
    def __init__(self, entries) -> None:
        self.entries = entries

    def list_documents(self):
        return list(self.entries)


class FakeDocumentLookupService:
    def __init__(self, graphs_by_id) -> None:
        self.graphs_by_id = graphs_by_id

    def get_document_graph(self, document_id: str, activity_context=None):
        return self.graphs_by_id.get(document_id)


class FakeVectorMappingRepository:
    def __init__(self, vectors_by_document) -> None:
        self.vectors_by_document = vectors_by_document

    def list_chunk_ids_by_document(self, document_id: str) -> list[str]:
        return list(self.vectors_by_document.get(document_id, []))


def test_corpus_statistics_workflow_aggregates_catalog_and_graph_details(
    sample_document_graph,
) -> None:
    entries = [
        DocumentCatalogEntry(
            document_id=sample_document_graph.document.document_id,
            title=sample_document_graph.document.title,
            file_name=sample_document_graph.document.file_name,
            file_path=sample_document_graph.document.file_path,
            document_type=sample_document_graph.document.document_type.value,
            language=None,
            page_count=4,
            chunk_count=1,
            section_count=1,
            identifier_count=1,
            table_count=1,
            picture_count=1,
            created_at=None,
        )
    ]
    workflow = CorpusStatisticsWorkflow(
        document_catalog_service=FakeDocumentCatalogService(entries),
        document_lookup_service=FakeDocumentLookupService(
            {sample_document_graph.document.document_id: sample_document_graph}
        ),
        vector_mapping_repository=FakeVectorMappingRepository(
            {sample_document_graph.document.document_id: ["chunk_001"]}
        ),
    )

    result = workflow.run()

    assert result.document_count == 1
    assert result.page_count == 4
    assert result.chunk_count == 1
    assert result.vector_count == 1
    assert result.documents_by_type == {"manual": 1}
    assert result.chunks_by_type == {"maintenance_interval": 1}
    assert result.identifiers_by_type == {"part_number": 1}
    assert result.diagnostics["graphs_loaded"] == 1
