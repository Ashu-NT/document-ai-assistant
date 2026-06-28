from pathlib import Path

from src.application.tools.retrieval import RetrieveChunksRequest, RetrieveChunksTool
from src.application.workflows.retrieval.tracing import RetrievalTraceWriter
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval import RetrievalQuery, RetrievalResult, RetrievedChunk


class FakeRetrievalWorkflow:
    def __init__(self) -> None:
        self.queries = []
        self.trace_recorders = []

    def run(self, query, activity_context=None, trace_recorder=None):
        self.queries.append(query)
        self.trace_recorders.append(trace_recorder)
        chunk = RetrievedChunk(
            chunk_id="chunk-1",
            document_id=query.document_id or "doc-1",
            content="Procedure content",
            score=0.91,
            retrieval_source="hybrid",
            chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
            source=SourceLocation(page_start=1, page_end=1),
        )
        result = RetrievalResult(
            result_id="res-1",
            query=query,
            chunks=[chunk],
            citations=[],
        )
        return RetrievalWorkflowResult(
            retrieval_result=result,
            enough_evidence=True,
            context_chunks=[chunk],
        )


def test_retrieve_chunks_tool_delegates_to_workflow_and_writes_trace(tmp_path: Path):
    workflow = FakeRetrievalWorkflow()
    tool = RetrieveChunksTool(
        retrieval_workflow=workflow,
        trace_writer=RetrievalTraceWriter(output_dir=tmp_path),
    )

    result = tool.run(
        RetrieveChunksRequest(
            query_text="maintenance interval",
            document_id="doc-1",
            top_k=3,
            trace=True,
        )
    )

    assert result.success is True
    assert workflow.queries[0].query_text == "maintenance interval"
    assert result.data["chunks"][0].chunk_id == "chunk-1"
    assert Path(result.data["trace_path"]).exists()

