import pytest

from src.application.workflows.ingestion import (
    DeleteDocumentNotSupportedError,
    DeleteDocumentWorkflow,
)


def test_delete_document_workflow_fails_cleanly_when_not_supported() -> None:
    workflow = DeleteDocumentWorkflow()

    with pytest.raises(DeleteDocumentNotSupportedError):
        workflow.run("doc_001")
