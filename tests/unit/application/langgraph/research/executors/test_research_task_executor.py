from types import SimpleNamespace

from src.application.langgraph.common import GraphError
from src.application.langgraph.research import ResearchTask, ResearchTaskExecutor
from src.application.langgraph.retrieval_strategy.models import RetrievalStrategy
from src.application.langgraph.factories import ToolRegistry
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class _FakeStrategyService:
    def __init__(self) -> None:
        self.contexts = []

    def select_and_plan(self, context, *, tool_registry):
        self.contexts.append(context)
        return SimpleNamespace(
            plan=SimpleNamespace(to_dict=lambda: {"steps": [{"tool_name": "retrieve_chunks"}]}),
            decision=SimpleNamespace(primary_strategy=RetrievalStrategy.MAINTENANCE_LOOKUP),
            trace={"primary_strategy": RetrievalStrategy.MAINTENANCE_LOOKUP.value},
        )


class _FakeExecutionResult:
    def __init__(self) -> None:
        self.success = True
        self.evidence_chunks = [
            RetrievedChunk(
                chunk_id="chunk-1",
                document_id="doc-42",
                content="Lubricate the bearings every 250 hours.",
                score=0.91,
                retrieval_source="hybrid",
                chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
                section_path=["6 Maintenance", "Lubrication"],
                source=SourceLocation(page_start=12, page_end=12),
            )
        ]
        self.tool_names = ["retrieve_chunks"]
        self.errors = []

    def to_dict(self) -> dict:
        return {"success": self.success}


class _FakePlanExecutor:
    def execute(self, plan, *, tool_registry, max_chunks):
        return _FakeExecutionResult()


class _FailingPlanExecutor:
    def execute(self, plan, *, tool_registry, max_chunks):
        raise GraphError(
            "Requested application tool is not configured.",
            error_code="tool_not_available",
            details={"tool_name": "retrieve_chunks"},
        )


def _task() -> ResearchTask:
    return ResearchTask(
        task_id="task-1",
        title="Collect maintenance tasks",
        question="What maintenance tasks are described?",
        strategy_hint=RetrievalStrategy.MAINTENANCE_LOOKUP.value,
        answer_intent_hint="maintenance_report",
        document_id="doc-42",
    )


def test_research_task_executor_collects_evidence() -> None:
    executor = ResearchTaskExecutor(
        retrieval_strategy_service=_FakeStrategyService(),
        retrieval_plan_executor=_FakePlanExecutor(),
    )

    result = executor.execute(
        _task(),
        route="deep_research",
        document_title="FWC12 Manual",
        tool_registry=ToolRegistry(retrieve_chunks_tool=object()),
        use_llm_strategy=False,
    )

    assert result.success is True
    assert result.retrieval_strategy == RetrievalStrategy.MAINTENANCE_LOOKUP.value
    assert result.tool_names == ["retrieve_chunks"]
    assert len(result.evidence) == 1
    assert result.evidence[0].chunk_id == "chunk-1"


def test_research_task_executor_forwards_identifier_value_from_task_diagnostics() -> None:
    strategy_service = _FakeStrategyService()
    executor = ResearchTaskExecutor(
        retrieval_strategy_service=strategy_service,
        retrieval_plan_executor=_FakePlanExecutor(),
    )
    task = ResearchTask(
        task_id="task-2",
        title="Collect evidence for MK311007",
        question="What evidence in this document describes MK311007?",
        strategy_hint=RetrievalStrategy.IDENTIFIER_LOOKUP.value,
        answer_intent_hint="identifier_lookup",
        document_id="doc-42",
        diagnostics={"concept": "MK311007", "identifier_value": "MK311007"},
    )

    executor.execute(
        task,
        route="deep_research",
        document_title="FWC12 Manual",
        tool_registry=ToolRegistry(retrieve_chunks_tool=object()),
        use_llm_strategy=False,
    )

    assert len(strategy_service.contexts) == 1
    assert strategy_service.contexts[0].identifier_value == "MK311007"


def test_research_task_executor_leaves_identifier_value_none_when_not_an_identifier_task() -> None:
    strategy_service = _FakeStrategyService()
    executor = ResearchTaskExecutor(
        retrieval_strategy_service=strategy_service,
        retrieval_plan_executor=_FakePlanExecutor(),
    )

    executor.execute(
        _task(),
        route="deep_research",
        document_title="FWC12 Manual",
        tool_registry=ToolRegistry(retrieve_chunks_tool=object()),
        use_llm_strategy=False,
    )

    assert strategy_service.contexts[0].identifier_value is None


def test_research_task_executor_returns_safe_failure_when_tool_is_missing() -> None:
    executor = ResearchTaskExecutor(
        retrieval_strategy_service=_FakeStrategyService(),
        retrieval_plan_executor=_FailingPlanExecutor(),
    )

    result = executor.execute(
        _task(),
        route="deep_research",
        document_title="FWC12 Manual",
        tool_registry=ToolRegistry(),
        use_llm_strategy=False,
    )

    assert result.success is False
    assert result.errors == ["tool_not_available"]
    assert result.diagnostics == {"tool_name": "retrieve_chunks"}
