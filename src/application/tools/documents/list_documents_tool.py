from __future__ import annotations

from dataclasses import dataclass

from src.application.services.document import DocumentCatalogService
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
)
from src.shared.exceptions import ApplicationError


def _entry_to_dict(entry) -> dict:
    return {
        "document_id": entry.document_id,
        "title": entry.title,
        "display_name": entry.title or entry.file_name,
        "file_name": entry.file_name,
        "file_path": entry.file_path,
        "document_type": entry.document_type,
        "language": entry.language,
        "page_count": entry.page_count,
        "chunk_count": entry.chunk_count,
        "section_count": entry.section_count,
        "identifier_count": entry.identifier_count,
        "table_count": entry.table_count,
        "picture_count": entry.picture_count,
        "ingested_at": (
            entry.created_at.isoformat() if entry.created_at is not None else None
        ),
    }


@dataclass(slots=True, kw_only=True)
class ListDocumentsRequest(ToolRequest):
    pass


class ListDocumentsTool:
    metadata = ToolMetadata(
        tool_name="list_documents",
        category="documents",
        description="List documents available in the seeded corpus.",
        mutates_state=False,
    )

    def __init__(self, document_catalog_service: DocumentCatalogService) -> None:
        self.document_catalog_service = document_catalog_service

    def run(self, request: ListDocumentsRequest) -> ToolResult:
        try:
            entries = self.document_catalog_service.list_documents()
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        return ToolResult.ok(
            data=[_entry_to_dict(entry) for entry in entries],
            message=f"Found {len(entries)} document(s).",
            diagnostics={"document_count": len(entries)},
            metadata=self.metadata,
        )
