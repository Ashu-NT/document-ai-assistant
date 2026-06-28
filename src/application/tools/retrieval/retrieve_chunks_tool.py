from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

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
from src.domain.common import ChunkType, DocumentType, new_id
from src.domain.retrieval import RetrievalQuery
from src.shared.exceptions import ApplicationError


@dataclass(slots=True, kw_only=True)
class RetrieveChunksRequest(ToolRequest):
    query_text: str | None = None
    document_id: str | None = None
    top_k: int = 5
    document_types: list[DocumentType] = field(default_factory=list)
    chunk_types: list[ChunkType] = field(default_factory=list)
    use_dense: bool = True
    use_keyword: bool = True
    use_sql: bool = True
    include_rejected: bool = False
    trace: bool = False


class RetrieveChunksTool:
    metadata = ToolMetadata(
        tool_name="retrieve_chunks",
        category="retrieval",
        description="Run the hybrid retrieval workflow and optionally emit a trace.",
        mutates_state=False,
        supports_trace=True,
    )

    def __init__(
        self,
        retrieval_workflow: RetrievalWorkflow,
        trace_writer: RetrievalTraceWriter | None = None,
    ) -> None:
        self.retrieval_workflow = retrieval_workflow
        self.trace_writer = trace_writer

    def run(self, request: RetrieveChunksRequest) -> ToolResult:
        if not request.query_text or not request.query_text.strip():
            return invalid_request_result(
                "query_text is required.",
                metadata=self.metadata,
            )

        query = RetrievalQuery(
            query_id=new_id("q"),
            query_text=request.query_text.strip(),
            document_types=list(request.document_types),
            chunk_types=list(request.chunk_types),
            document_id=request.document_id,
            top_k=request.top_k,
            use_dense=request.use_dense,
            use_keyword=request.use_keyword,
            use_sql=request.use_sql,
        )

        recorder = RetrievalTraceRecorder() if request.trace else None
        try:
            workflow_result = self.retrieval_workflow.run(
                query,
                trace_recorder=recorder,
            )
        except ApplicationError as exc:
            return application_error_result(
                exc,
                metadata=self.metadata,
                fallback_error_code="retrieval_failed",
            )

        trace_path = None
        if recorder is not None and self.trace_writer is not None:
            trace = recorder.build(
                query_id=query.query_id,
                timestamp_iso=datetime.now(timezone.utc).isoformat(),
            )
            trace_path = str(self.trace_writer.write(trace))

        diagnostics = {
            "result_count": workflow_result.result_count,
            "context_result_count": workflow_result.context_result_count,
            "enough_evidence": workflow_result.enough_evidence,
            "include_rejected_requested": request.include_rejected,
            "trace_path": trace_path,
        }
        return ToolResult.ok(
            data={
                "workflow_result": workflow_result,
                "query": workflow_result.query,
                "chunks": workflow_result.chunks,
                "context_chunks": workflow_result.final_chunks,
                "citations": workflow_result.retrieval_result.citations,
                "guardrail_result": workflow_result.guardrail_result,
                "trace_path": trace_path,
            },
            diagnostics=diagnostics,
            metadata=self.metadata,
        )
