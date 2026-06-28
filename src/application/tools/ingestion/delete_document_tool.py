from __future__ import annotations

from dataclasses import dataclass

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    not_implemented_result,
)


@dataclass(slots=True, kw_only=True)
class DeleteDocumentRequest(ToolRequest):
    document_id: str | None = None


class DeleteDocumentTool:
    metadata = ToolMetadata(
        tool_name="delete_document",
        category="ingestion",
        description="Reserved for safe delete or archive workflow integration.",
        mutates_state=True,
    )

    def run(self, request: DeleteDocumentRequest) -> ToolResult:
        return not_implemented_result(
            metadata=self.metadata,
            message="Safe document deletion is not supported by the current application services.",
        )
