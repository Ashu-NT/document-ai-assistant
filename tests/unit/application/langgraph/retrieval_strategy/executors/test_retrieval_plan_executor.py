from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.retrieval_strategy.executors import RetrievalPlanExecutor
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalPlan,
    RetrievalPlanStep,
    RetrievalStrategy,
)
from src.application.tools.common import ToolResult
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval import RetrievedChunk


class _FakeTool:
    def __init__(self, chunks):
        self.chunks = chunks
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(
            data={
                "chunks": list(self.chunks),
                "context_chunks": list(self.chunks),
            }
        )


def test_retrieval_plan_executor_executes_steps_and_merges_evidence() -> None:
    chunk_a = RetrievedChunk(
        chunk_id="chunk-a",
        document_id="doc-1",
        content="Maintenance interval is 500 hours.",
        score=0.91,
        retrieval_source="table",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        source=SourceLocation(page_start=12, page_end=12),
    )
    chunk_b = RetrievedChunk(
        chunk_id="chunk-b",
        document_id="doc-1",
        content="Service schedule table.",
        score=0.88,
        retrieval_source="chunk",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        source=SourceLocation(page_start=13, page_end=13),
    )
    table_tool = _FakeTool([chunk_a])
    chunk_tool = _FakeTool([chunk_a, chunk_b])
    plan = RetrievalPlan(
        plan_id="plan-1",
        original_query="maintenance schedule",
        document_id="doc-1",
        primary_strategy=RetrievalStrategy.MAINTENANCE_LOOKUP,
        steps=[
            RetrievalPlanStep(
                step_id="step-1",
                strategy=RetrievalStrategy.TABLE_LOOKUP,
                query="maintenance schedule table",
                document_id="doc-1",
                top_k=5,
                tool_name="retrieve_tables",
                args={"query_text": "maintenance schedule table", "document_id": "doc-1", "top_k": 5},
                output_key="step_1",
            ),
            RetrievalPlanStep(
                step_id="step-2",
                strategy=RetrievalStrategy.MAINTENANCE_LOOKUP,
                query="maintenance schedule",
                document_id="doc-1",
                top_k=5,
                tool_name="retrieve_chunks",
                args={"query_text": "maintenance schedule", "document_id": "doc-1", "top_k": 5},
                output_key="step_2",
                required=False,
            ),
        ],
    )

    result = RetrievalPlanExecutor().execute(
        plan,
        tool_registry=ToolRegistry(
            retrieve_chunks_tool=chunk_tool,
            retrieve_tables_tool=table_tool,
        ),
        max_chunks=10,
    )

    assert result.success is True
    assert table_tool.requests
    assert chunk_tool.requests
    assert [chunk.chunk_id for chunk in result.evidence_chunks] == ["chunk-a", "chunk-b"]
    assert result.context_document_ids == ["doc-1"]
