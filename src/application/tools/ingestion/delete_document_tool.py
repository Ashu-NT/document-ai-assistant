from __future__ import annotations

from dataclasses import dataclass

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.application.workflows.ingestion import DeleteDocumentWorkflow
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class DeleteDocumentRequest(ToolRequest):
    document_id: str | None = None


class DeleteDocumentTool:
    metadata = ToolMetadata(
        tool_name="delete_document",
        category="ingestion",
        description="Reserved for safe delete or archive workflow integration.",
        mutates_state=True,
    )

    def __init__(self, delete_document_workflow: DeleteDocumentWorkflow) -> None:
        self.delete_document_workflow = delete_document_workflow

    def run(self, request: DeleteDocumentRequest) -> ToolResult:
        if not request.document_id or not request.document_id.strip():
            return invalid_request_result(
                "document_id is required.",
                metadata=self.metadata,
            )

        try:
            self.delete_document_workflow.run(request.document_id)
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        return ToolResult.ok(
            data={"document_id": request.document_id},
            metadata=self.metadata,
        )
