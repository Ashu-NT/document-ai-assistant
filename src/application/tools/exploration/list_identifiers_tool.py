from __future__ import annotations

from dataclasses import dataclass

from src.application.services.document import DocumentLookupService
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
class ListIdentifiersRequest(ToolRequest):
    document_id: str | None = None
    identifier_value: str | None = None


class ListIdentifiersTool:
    metadata = ToolMetadata(
        tool_name="list_identifiers",
        category="exploration",
        description="List identifiers for one document or by exact identifier value.",
        mutates_state=False,
    )

    def __init__(
        self,
        exploration_service: DocumentExplorationService,
        document_lookup_service: DocumentLookupService,
    ) -> None:
        self.exploration_service = exploration_service
        self.document_lookup_service = document_lookup_service

    def run(self, request: ListIdentifiersRequest) -> ToolResult:
        if request.document_id:
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
            return ToolResult.ok(data=result.identifiers, metadata=self.metadata)

        if request.identifier_value and request.identifier_value.strip():
            try:
                identifiers = self.document_lookup_service.search_identifiers(
                    request.identifier_value
                )
            except ApplicationError as exc:
                return application_error_result(exc, metadata=self.metadata)
            return ToolResult.ok(data=identifiers, metadata=self.metadata)

        return invalid_request_result(
            "Provide document_id or identifier_value.",
            metadata=self.metadata,
        )
