from __future__ import annotations

from dataclasses import dataclass

from src.application.services.document import DocumentCatalogService
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.application.tools.documents.list_documents_tool import _entry_to_dict
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class DocumentDetailsRequest(ToolRequest):
    document_id: str | None = None


class DocumentDetailsTool:
    metadata = ToolMetadata(
        tool_name="document_details",
        category="documents",
        description="Return lightweight document metadata without loading the full graph.",
        mutates_state=False,
    )

    def __init__(self, document_catalog_service: DocumentCatalogService) -> None:
        self.document_catalog_service = document_catalog_service

    def run(self, request: DocumentDetailsRequest) -> ToolResult:
        if not request.document_id:
            return invalid_request_result(
                "document_id is required.",
                metadata=self.metadata,
            )

        try:
            entry = self.document_catalog_service.get_document(request.document_id)
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        if entry is None:
            return ToolResult.fail(
                "Document was not found.",
                error_code="document_not_found",
                diagnostics={"document_id": request.document_id},
                metadata=self.metadata,
            )

        data = _entry_to_dict(entry)
        data["graph_available"] = True
        return ToolResult.ok(data=data, metadata=self.metadata)
