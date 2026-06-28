from __future__ import annotations

from dataclasses import dataclass

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    not_implemented_result,
)


@dataclass(slots=True, kw_only=True)
class ExplainAnswerRequest(ToolRequest):
    pass


class ExplainAnswerTool:
    metadata = ToolMetadata(
        tool_name="explain_answer",
        category="question_answering",
        description="Reserved for future answer explanation support.",
        requires_llm=False,
        mutates_state=False,
    )

    def run(self, request: ExplainAnswerRequest) -> ToolResult:
        return not_implemented_result(
            metadata=self.metadata,
            message="Answer explanation is not implemented as a separate application capability yet.",
        )
