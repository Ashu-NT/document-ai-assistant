from __future__ import annotations

from dataclasses import dataclass

from src.application.services.document_exploration import (
    DocumentExplorationService,
    DocumentNotFoundError,
)
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class DocumentSummaryRequest(ToolRequest):
    document_id: str | None = None


class DocumentSummaryTool:
    metadata = ToolMetadata(
        tool_name="document_summary",
        category="exploration",
        description="Build a deterministic document summary from overview and sections.",
        mutates_state=False,
    )

    def __init__(self, exploration_service: DocumentExplorationService) -> None:
        self.exploration_service = exploration_service

    def run(self, request: DocumentSummaryRequest) -> ToolResult:
        if not request.document_id:
            return invalid_request_result(
                "document_id is required.",
                metadata=self.metadata,
            )

        try:
            result = self.exploration_service.explore(request.document_id)
        except DocumentNotFoundError:
            return ToolResult.fail(
                "Document was not found.",
                error_code="document_not_found",
                diagnostics={"document_id": request.document_id},
                metadata=self.metadata,
            )
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        overview = result.overview
        top_sections = [section.title for section in result.sections[:5]]
        summary_lines = [
            f"{overview.title or overview.file_name} ({overview.document_type})",
            f"Pages: {overview.page_count or '-'} | Sections: {overview.section_count} | Chunks: {overview.chunk_count}",
            f"Identifiers: {overview.identifier_count} | Tables: {overview.table_count} | Pictures: {overview.picture_count}",
        ]
        if top_sections:
            summary_lines.append(f"Top sections: {', '.join(top_sections)}")

        return ToolResult.ok(
            data={
                "document_id": result.document_id,
                "overview": overview,
                "coverage": result.coverage,
                "summary_text": "\n".join(summary_lines),
            },
            metadata=self.metadata,
        )
