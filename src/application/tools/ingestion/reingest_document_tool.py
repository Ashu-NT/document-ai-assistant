from __future__ import annotations

from dataclasses import dataclass

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    not_implemented_result,
)


@dataclass(slots=True, kw_only=True)
class ReingestDocumentRequest(ToolRequest):
    document_id: str | None = None
    file_path: str | None = None


class ReingestDocumentTool:
    metadata = ToolMetadata(
        tool_name="reingest_document",
        category="ingestion",
        description="Reserved for safe reingestion workflow integration.",
        mutates_state=True,
    )

    def run(self, request: ReingestDocumentRequest) -> ToolResult:
        return not_implemented_result(
            metadata=self.metadata,
            message="Document reingestion is not implemented as a safe application workflow yet.",
        )
