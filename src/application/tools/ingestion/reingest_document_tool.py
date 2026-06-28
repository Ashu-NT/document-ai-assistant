from __future__ import annotations

from dataclasses import dataclass

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.application.workflows.ingestion import IngestionWorkflow, ReingestionRequest
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class ReingestDocumentRequest(ToolRequest):
    document_id: str | None = None
    file_path: str | None = None


class ReingestDocumentTool:
    metadata = ToolMetadata(
        tool_name="reingest_document",
        category="ingestion",
        description="Reserved for safe reingestion workflow integration.",
        mutates_state=True,
    )

    def __init__(self, ingestion_workflow: IngestionWorkflow) -> None:
        self.ingestion_workflow = ingestion_workflow

    def run(self, request: ReingestDocumentRequest) -> ToolResult:
        if not request.document_id or not request.document_id.strip():
            return invalid_request_result(
                "document_id is required.",
                metadata=self.metadata,
            )

        try:
            result = self.ingestion_workflow.reingest(
                ReingestionRequest(
                    document_id=request.document_id,
                    requested_by=request.user_id,
                    correlation_id=request.request_id,
                )
            )
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        return ToolResult.ok(data=result, metadata=self.metadata)
