from src.application.tools.ingestion import (
    DeleteDocumentRequest,
    DeleteDocumentTool,
    IngestDocumentRequest,
    IngestDocumentTool,
)


def test_ingest_document_tool_fails_safely_when_not_wired():
    result = IngestDocumentTool().run(
        IngestDocumentRequest(file_path="manual.pdf")
    )

    assert result.success is False
    assert result.error_code == "not_implemented"


def test_delete_document_tool_fails_safely_when_not_supported():
    result = DeleteDocumentTool().run(
        DeleteDocumentRequest(document_id="doc-1")
    )

    assert result.success is False
    assert result.error_code == "not_implemented"
