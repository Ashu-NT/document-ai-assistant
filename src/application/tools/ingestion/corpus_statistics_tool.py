from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.application.services.document import DocumentCatalogService
from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
)
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class CorpusStatisticsRequest(ToolRequest):
    pass


class CorpusStatisticsTool:
    metadata = ToolMetadata(
        tool_name="corpus_statistics",
        category="ingestion",
        description="Return aggregate corpus statistics without mutating state.",
        mutates_state=False,
    )

    def __init__(self, document_catalog_service: DocumentCatalogService) -> None:
        self.document_catalog_service = document_catalog_service

    def run(self, request: CorpusStatisticsRequest) -> ToolResult:
        try:
            documents = self.document_catalog_service.list_documents()
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        document_type_counts = Counter(entry.document_type for entry in documents)
        data = {
            "document_count": len(documents),
            "page_count": sum(entry.page_count or 0 for entry in documents),
            "chunk_count": sum(entry.chunk_count for entry in documents),
            "section_count": sum(entry.section_count for entry in documents),
            "identifier_count": sum(entry.identifier_count for entry in documents),
            "table_count": sum(entry.table_count for entry in documents),
            "picture_count": sum(entry.picture_count for entry in documents),
            "document_type_counts": dict(document_type_counts),
        }
        return ToolResult.ok(data=data, metadata=self.metadata)
