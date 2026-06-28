from types import SimpleNamespace

from src.application.tools.documents import (
    DocumentDetailsRequest,
    DocumentDetailsTool,
    DocumentStatisticsRequest,
    DocumentStatisticsTool,
    FindDocumentRequest,
    FindDocumentTool,
    ListDocumentsRequest,
    ListDocumentsTool,
)


class FakeDocumentCatalogService:
    def __init__(self, entries):
        self.entries = list(entries)

    def list_documents(self):
        return list(self.entries)

    def find_documents(self, query_text: str):
        query = query_text.lower()
        return [
            entry
            for entry in self.entries
            if query in (entry.title or "").lower() or query in entry.file_name.lower()
        ]

    def get_document(self, document_id: str):
        return next(
            (entry for entry in self.entries if entry.document_id == document_id),
            None,
        )

    def get_latest_document(self):
        return self.entries[0] if self.entries else None


class FakeDocumentLookupService:
    def __init__(self, graph):
        self.graph = graph
        self.requested_document_id = None

    def get_document_graph(self, document_id: str):
        self.requested_document_id = document_id
        return self.graph


def _entry(document_id: str, title: str = "Manual") -> SimpleNamespace:
    return SimpleNamespace(
        document_id=document_id,
        title=title,
        file_name=f"{title}.pdf",
        file_path=f"docs/{title}.pdf",
        document_type="manual",
        language="en",
        page_count=10,
        chunk_count=5,
        section_count=3,
        identifier_count=2,
        table_count=1,
        picture_count=0,
        created_at=None,
    )


def _graph() -> SimpleNamespace:
    return SimpleNamespace(
        document=SimpleNamespace(
            document_id="doc-1",
            title="Manual",
            file_name="Manual.pdf",
            document_type="manual",
            statistics=SimpleNamespace(
                page_count=10,
                section_count=3,
                chunk_count=5,
                table_count=1,
                picture_count=0,
                identifier_count=2,
                chunk_type_counts={"general": 3, "overview": 2},
            ),
        )
    )


def test_list_documents_tool_delegates_to_catalog_service():
    tool = ListDocumentsTool(FakeDocumentCatalogService([_entry("doc-1")]))

    result = tool.run(ListDocumentsRequest())

    assert result.success is True
    assert result.data[0]["document_id"] == "doc-1"
    assert result.diagnostics["document_count"] == 1


def test_find_document_tool_resolves_by_id():
    tool = FindDocumentTool(FakeDocumentCatalogService([_entry("doc-1")]))

    result = tool.run(FindDocumentRequest(document_id="doc-1"))

    assert result.success is True
    assert result.data["display_name"] == "Manual"


def test_find_document_tool_handles_multiple_matches():
    tool = FindDocumentTool(
        FakeDocumentCatalogService([_entry("doc-1", "Pump Manual"), _entry("doc-2", "Pump Guide")])
    )

    result = tool.run(FindDocumentRequest(query_text="Pump"))

    assert result.success is False
    assert result.error_code == "multiple_documents_found"
    assert len(result.diagnostics["matches"]) == 2


def test_document_details_tool_returns_lightweight_metadata():
    tool = DocumentDetailsTool(FakeDocumentCatalogService([_entry("doc-1")]))

    result = tool.run(DocumentDetailsRequest(document_id="doc-1"))

    assert result.success is True
    assert result.data["graph_available"] is True
    assert result.data["file_path"] == "docs/Manual.pdf"


def test_document_statistics_tool_returns_counts():
    lookup_service = FakeDocumentLookupService(_graph())
    tool = DocumentStatisticsTool(
        document_lookup_service=lookup_service,
        document_catalog_service=FakeDocumentCatalogService([_entry("doc-1")]),
    )

    result = tool.run(DocumentStatisticsRequest(document_id="doc-1"))

    assert result.success is True
    assert lookup_service.requested_document_id == "doc-1"
    assert result.data["chunk_type_counts"] == {"general": 3, "overview": 2}
    assert result.data["chunk_count"] == 5
