from src.application.services.document_exploration.document_exploration_result import (
    DocumentCoverage,
    DocumentExplorationResult,
    DocumentOverview,
    SectionEntry,
)
from src.application.tools.exploration import (
    DocumentSummaryRequest,
    DocumentSummaryTool,
    ExploreDocumentRequest,
    ExploreDocumentTool,
    ListSectionsRequest,
    ListSectionsTool,
)


class FakeExplorationService:
    def __init__(self, result: DocumentExplorationResult) -> None:
        self.result = result
        self.requested_document_ids: list[str] = []

    def explore(self, document_id: str) -> DocumentExplorationResult:
        self.requested_document_ids.append(document_id)
        return self.result


def _exploration_result() -> DocumentExplorationResult:
    return DocumentExplorationResult(
        document_id="doc-1",
        overview=DocumentOverview(
            document_id="doc-1",
            title="Pump Manual",
            file_name="manual.pdf",
            document_type="manual",
            language="en",
            page_count=12,
            section_count=2,
            chunk_count=4,
            table_count=1,
            picture_count=0,
            identifier_count=1,
        ),
        sections=[
            SectionEntry(
                section_id="sec-1",
                title="Maintenance",
                level=1,
                parent_section_id=None,
                section_path=["Maintenance"],
            )
        ],
        coverage=DocumentCoverage(
            chunk_type_counts={"maintenance_procedure": 2},
            has_tables=True,
            has_pictures=False,
            has_identifiers=True,
            has_sections=True,
        ),
    )


def test_explore_document_tool_delegates_to_service():
    service = FakeExplorationService(_exploration_result())
    tool = ExploreDocumentTool(service)

    result = tool.run(ExploreDocumentRequest(document_id="doc-1"))

    assert result.success is True
    assert service.requested_document_ids == ["doc-1"]
    assert result.data.document_id == "doc-1"


def test_list_sections_tool_returns_section_hierarchy():
    tool = ListSectionsTool(FakeExplorationService(_exploration_result()))

    result = tool.run(ListSectionsRequest(document_id="doc-1"))

    assert result.success is True
    assert result.data[0].title == "Maintenance"


def test_document_summary_tool_builds_deterministic_summary():
    tool = DocumentSummaryTool(FakeExplorationService(_exploration_result()))

    result = tool.run(DocumentSummaryRequest(document_id="doc-1"))

    assert result.success is True
    assert "Pump Manual" in result.data["summary_text"]
    assert "Top sections: Maintenance" in result.data["summary_text"]
