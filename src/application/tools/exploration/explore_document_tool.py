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
class ExploreDocumentRequest(ToolRequest):
    document_id: str | None = None


class ExploreDocumentTool:
    metadata = ToolMetadata(
        tool_name="explore_document",
        category="exploration",
        description="Explore a document graph deterministically.",
        mutates_state=False,
    )

    def __init__(self, exploration_service: DocumentExplorationService) -> None:
        self.exploration_service = exploration_service

    def run(self, request: ExploreDocumentRequest) -> ToolResult:
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

        return ToolResult.ok(data=result, metadata=self.metadata)
