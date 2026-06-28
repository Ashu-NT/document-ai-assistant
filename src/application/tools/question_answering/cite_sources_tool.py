from __future__ import annotations

from dataclasses import dataclass

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    not_implemented_result,
)


@dataclass(slots=True, kw_only=True)
class CiteSourcesRequest(ToolRequest):
    pass


class CiteSourcesTool:
    metadata = ToolMetadata(
        tool_name="cite_sources",
        category="question_answering",
        description="Reserved for future source citation post-processing support.",
        requires_llm=False,
        mutates_state=False,
    )

    def run(self, request: CiteSourcesRequest) -> ToolResult:
        return not_implemented_result(
            metadata=self.metadata,
            message="Source citation post-processing is not implemented as a standalone tool yet.",
        )
