from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.application.tools.common import (
    ToolMetadata,
    ToolRequest,
    ToolResult,
    application_error_result,
    invalid_request_result,
)
from src.application.workflows.retrieval import RetrievalWorkflow
from src.application.workflows.retrieval.tracing import (
    RetrievalTraceRecorder,
    RetrievalTraceWriter,
)
from src.domain.common import new_id
from src.domain.retrieval import RetrievalQuery
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class RetrievalTraceRequest(ToolRequest):
    trace_path: str | None = None
    query_text: str | None = None
    document_id: str | None = None
    top_k: int = 5
    write_output: bool = True


class RetrievalTraceTool:
    metadata = ToolMetadata(
        tool_name="retrieval_trace",
        category="evaluation",
        description="Create or read retrieval trace JSON output.",
        mutates_state=False,
        supports_trace=True,
    )

    def __init__(
        self,
        retrieval_workflow: RetrievalWorkflow,
        trace_writer: RetrievalTraceWriter | None = None,
    ) -> None:
        self.retrieval_workflow = retrieval_workflow
        self.trace_writer = trace_writer or RetrievalTraceWriter()

    def run(self, request: RetrievalTraceRequest) -> ToolResult:
        if request.trace_path:
            path = Path(request.trace_path)
            if not path.exists():
                return ToolResult.fail(
                    "Retrieval trace file was not found.",
                    error_code="document_not_found",
                    diagnostics={"trace_path": str(path)},
                    metadata=self.metadata,
                )
            return ToolResult.ok(
                data=json.loads(path.read_text(encoding="utf-8")),
                metadata=self.metadata,
            )

        if not request.query_text or not request.query_text.strip():
            return invalid_request_result(
                "Provide trace_path or query_text.",
                metadata=self.metadata,
            )

        query = RetrievalQuery(
            query_id=new_id("q"),
            query_text=request.query_text.strip(),
            document_id=request.document_id,
            top_k=request.top_k,
        )
        recorder = RetrievalTraceRecorder()
        try:
            result = self.retrieval_workflow.run(query, trace_recorder=recorder)
        except ApplicationError as exc:
            return application_error_result(
                exc,
                metadata=self.metadata,
                fallback_error_code="retrieval_failed",
            )

        trace = recorder.build(
            query_id=query.query_id,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
        )
        trace_path = None
        if request.write_output:
            trace_path = str(self.trace_writer.write(trace))

        return ToolResult.ok(
            data={
                "trace": self._load_trace_payload(trace_path) if trace_path else trace,
                "trace_path": trace_path,
                "result_count": result.result_count,
                "context_result_count": result.context_result_count,
            },
            metadata=self.metadata,
        )

    @staticmethod
    def _load_trace_payload(trace_path: str) -> dict[str, Any]:
        return json.loads(Path(trace_path).read_text(encoding="utf-8"))
