from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.application.workflows.ingestion import IngestionRequest, IngestionWorkflow
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class IngestDocumentRequest(ToolRequest):
    file_path: str | None = None
    document_type: str | None = None
    title: str | None = None
    source_name: str | None = None
    force: bool = False
    extra_metadata: dict[str, Any] = field(default_factory=dict)
    generate_questions: bool | None = None
    enable_ocr: bool | None = None
    run_quality_checks: bool = True
    trace: bool = False


class IngestDocumentTool:
    metadata = ToolMetadata(
        tool_name="ingest_document",
        category="ingestion",
        description="Reserved for safe ingestion workflow integration.",
        mutates_state=True,
    )

    def __init__(self, ingestion_workflow: IngestionWorkflow) -> None:
        self.ingestion_workflow = ingestion_workflow

    def run(self, request: IngestDocumentRequest) -> ToolResult:
        if not request.file_path or not request.file_path.strip():
            return invalid_request_result(
                "file_path is required.",
                metadata=self.metadata,
            )

        try:
            result = self.ingestion_workflow.run(
                IngestionRequest(
                    file_path=request.file_path,
                    document_type=request.document_type,
                    title=request.title,
                    source_name=request.source_name,
                    metadata=dict(request.extra_metadata),
                    force=request.force,
                    generate_questions=request.generate_questions,
                    enable_ocr=request.enable_ocr,
                    run_quality_checks=request.run_quality_checks,
                    trace=request.trace,
                    requested_by=request.user_id,
                    correlation_id=request.request_id,
                )
            )
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        return ToolResult.ok(data=result, metadata=self.metadata)
