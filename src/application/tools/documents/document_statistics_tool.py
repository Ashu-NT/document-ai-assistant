from __future__ import annotations

from dataclasses import dataclass

from src.application.services.document import DocumentCatalogService, DocumentLookupService
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class DocumentStatisticsRequest(ToolRequest):
    document_id: str | None = None


class DocumentStatisticsTool:
    metadata = ToolMetadata(
        tool_name="document_statistics",
        category="documents",
        description="Return document and chunk statistics for a document graph.",
        mutates_state=False,
    )

    def __init__(
        self,
        document_lookup_service: DocumentLookupService,
        document_catalog_service: DocumentCatalogService | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.document_catalog_service = document_catalog_service

    def run(self, request: DocumentStatisticsRequest) -> ToolResult:
        if not request.document_id:
            return invalid_request_result(
                "document_id is required.",
                metadata=self.metadata,
            )

        try:
            graph = self.document_lookup_service.get_document_graph(request.document_id)
            entry = (
                self.document_catalog_service.get_document(request.document_id)
                if self.document_catalog_service is not None
                else None
            )
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        if graph is None:
            return ToolResult.fail(
                "Document was not found.",
                error_code="document_not_found",
                diagnostics={"document_id": request.document_id},
                metadata=self.metadata,
            )

        stats = graph.document.statistics
        data = {
            "document_id": graph.document.document_id,
            "title": graph.document.title,
            "file_name": graph.document.file_name,
            "document_type": str(graph.document.document_type),
            "page_count": (
                entry.page_count
                if entry is not None and entry.page_count is not None
                else stats.page_count
            ),
            "section_count": max(stats.section_count, entry.section_count if entry else 0),
            "chunk_count": max(stats.chunk_count, entry.chunk_count if entry else 0),
            "table_count": max(stats.table_count, entry.table_count if entry else 0),
            "picture_count": max(
                stats.picture_count,
                entry.picture_count if entry else 0,
            ),
            "identifier_count": max(
                stats.identifier_count,
                entry.identifier_count if entry else 0,
            ),
            "chunk_type_counts": dict(stats.chunk_type_counts),
        }
        return ToolResult.ok(data=data, metadata=self.metadata)
