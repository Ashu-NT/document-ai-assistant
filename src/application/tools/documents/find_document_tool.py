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
class FindDocumentRequest(ToolRequest):
    document_id: str | None = None
    query_text: str | None = None
    latest: bool = False
    allow_multiple: bool = False


class FindDocumentTool:
    metadata = ToolMetadata(
        tool_name="find_document",
        category="documents",
        description="Resolve a document by ID, partial title or file name, or latest.",
        mutates_state=False,
    )

    def __init__(self, document_catalog_service: DocumentCatalogService) -> None:
        self.document_catalog_service = document_catalog_service

    def run(self, request: FindDocumentRequest) -> ToolResult:
        selector_count = sum(
            1
            for value in (
                bool(request.document_id),
                bool(request.query_text and request.query_text.strip()),
                request.latest,
            )
            if value
        )
        if selector_count != 1:
            return invalid_request_result(
                "Provide exactly one selector: document_id, query_text, or latest.",
                metadata=self.metadata,
                diagnostics={
                    "document_id": request.document_id,
                    "query_text": request.query_text,
                    "latest": request.latest,
                },
            )

        try:
            if request.document_id:
                entry = self.document_catalog_service.get_document(request.document_id)
                if entry is None:
                    return ToolResult.fail(
                        "Document was not found.",
                        error_code="document_not_found",
                        diagnostics={"document_id": request.document_id},
                        metadata=self.metadata,
                    )
                return ToolResult.ok(
                    data=_entry_to_dict(entry),
                    metadata=self.metadata,
                )

            if request.latest:
                entry = self.document_catalog_service.get_latest_document()
                if entry is None:
                    return ToolResult.fail(
                        "No documents are available in the corpus.",
                        error_code="document_not_found",
                        metadata=self.metadata,
                    )
                return ToolResult.ok(
                    data=_entry_to_dict(entry),
                    metadata=self.metadata,
                )

            matches = self.document_catalog_service.find_documents(
                request.query_text or ""
            )
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        if not matches:
            return ToolResult.fail(
                "Document was not found.",
                error_code="document_not_found",
                diagnostics={"query_text": request.query_text},
                metadata=self.metadata,
            )

        if len(matches) > 1 and not request.allow_multiple:
            return ToolResult.fail(
                "Multiple documents matched the query.",
                error_code="multiple_documents_found",
                diagnostics={
                    "query_text": request.query_text,
                    "matches": [_entry_to_dict(entry) for entry in matches],
                },
                metadata=self.metadata,
            )

        payload = [_entry_to_dict(entry) for entry in matches]
        return ToolResult.ok(
            data=payload if request.allow_multiple else payload[0],
            diagnostics={"match_count": len(matches)},
            metadata=self.metadata,
        )
