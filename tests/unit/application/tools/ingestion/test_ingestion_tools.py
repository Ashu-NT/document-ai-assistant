from src.application.tools.ingestion import (
    CorpusStatisticsRequest,
    CorpusStatisticsTool,
    DeleteDocumentRequest,
    DeleteDocumentTool,
    IngestDocumentRequest,
    IngestDocumentTool,
    ReingestDocumentRequest,
    ReingestDocumentTool,
)
from src.application.workflows.ingestion import (
    CorpusStatisticsResult,
    DeleteDocumentNotSupportedError,
    IngestionResult,
    IngestionStatus,
    ReingestionNotSupportedError,
)


class FakeIngestionWorkflow:
    def __init__(self) -> None:
        self.run_calls = []
        self.reingest_calls = []

    def run(self, request):
        self.run_calls.append(request)
        return IngestionResult(
            status=IngestionStatus.COMPLETE,
            document_id="doc_001",
            file_name="manual.pdf",
        )

    def reingest(self, request):
        self.reingest_calls.append(request)
        raise ReingestionNotSupportedError(
            "Reingestion is not implemented safely yet.",
            error_code="reingestion_not_supported",
        )


class FakeDeleteDocumentWorkflow:
    def __init__(self) -> None:
        self.calls = []

    def run(self, document_id: str):
        self.calls.append(document_id)
        raise DeleteDocumentNotSupportedError(
            "Document deletion is not implemented safely yet.",
            error_code="delete_not_supported",
        )


class FakeCorpusStatisticsWorkflow:
    def __init__(self) -> None:
        self.calls = 0

    def run(self):
        self.calls += 1
        return CorpusStatisticsResult(
            document_count=1,
            page_count=10,
            section_count=3,
            chunk_count=7,
            vector_count=7,
            documents_by_type={"manual": 1},
            chunks_by_type={"maintenance_interval": 2},
            identifiers_by_type={"part_number": 1},
            failed_ingestion_count=None,
        )


def test_ingest_document_tool_delegates_to_workflow():
    workflow = FakeIngestionWorkflow()
    result = IngestDocumentTool(workflow).run(
        IngestDocumentRequest(
            file_path="manual.pdf",
            document_type="manual",
            generate_questions=True,
        )
    )

    assert result.success is True
    assert result.data.document_id == "doc_001"
    assert workflow.run_calls[0].file_path == "manual.pdf"
    assert workflow.run_calls[0].document_type == "manual"
    assert workflow.run_calls[0].generate_questions is True


def test_ingest_document_tool_rejects_missing_file_path():
    workflow = FakeIngestionWorkflow()
    result = IngestDocumentTool(workflow).run(IngestDocumentRequest())

    assert result.success is False
    assert result.error_code == "invalid_request"


def test_reingest_document_tool_returns_application_error():
    workflow = FakeIngestionWorkflow()
    result = ReingestDocumentTool(workflow).run(
        ReingestDocumentRequest(document_id="doc_001")
    )

    assert result.success is False
    assert result.error_code == "reingestion_not_supported"
    assert workflow.reingest_calls[0].document_id == "doc_001"


def test_delete_document_tool_fails_safely_when_not_supported():
    workflow = FakeDeleteDocumentWorkflow()
    result = DeleteDocumentTool(workflow).run(
        DeleteDocumentRequest(document_id="doc-1")
    )

    assert result.success is False
    assert result.error_code == "delete_not_supported"
    assert workflow.calls == ["doc-1"]


def test_corpus_statistics_tool_delegates_to_workflow():
    workflow = FakeCorpusStatisticsWorkflow()
    result = CorpusStatisticsTool(workflow).run(CorpusStatisticsRequest())

    assert result.success is True
    assert result.data.document_count == 1
    assert workflow.calls == 1
