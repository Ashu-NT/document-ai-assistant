from __future__ import annotations

from dataclasses import dataclass

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
)
from src.application.workflows.ingestion import CorpusStatisticsWorkflow
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

    def __init__(self, corpus_statistics_workflow: CorpusStatisticsWorkflow) -> None:
        self.corpus_statistics_workflow = corpus_statistics_workflow

    def run(self, request: CorpusStatisticsRequest) -> ToolResult:
        try:
            result = self.corpus_statistics_workflow.run()
        except ApplicationError as exc:
            return application_error_result(exc, metadata=self.metadata)

        return ToolResult.ok(data=result, metadata=self.metadata)
