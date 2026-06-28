from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    not_implemented_result,
)


@dataclass(slots=True, kw_only=True)
class IngestDocumentRequest(ToolRequest):
    file_path: str | None = None
    document_type: str | None = None
    force: bool = False
    extra_metadata: dict[str, Any] = field(default_factory=dict)


class IngestDocumentTool:
    metadata = ToolMetadata(
        tool_name="ingest_document",
        category="ingestion",
        description="Reserved for safe ingestion workflow integration.",
        mutates_state=True,
    )

    def run(self, request: IngestDocumentRequest) -> ToolResult:
        return not_implemented_result(
            metadata=self.metadata,
            message="Document ingestion is not wired to a safe application workflow yet.",
        )
