import json

from src.application.contracts.ai import LLMGenerationResult
from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.batching.extraction_chunk_batcher import (
    ExtractionChunkBatcher,
)
from src.application.workflows.extraction.extraction_execution_strategy import (
    ExtractionExecutionStrategy,
)
from src.domain.assets import TableAsset
from tests.unit.application.workflows.extraction._test_extraction_workflow_support_part1 import (
    FakeExtractionService,
    clone_chunk,
    make_workflow,
    _empty_extraction_response,
)

_TABLE_HEADER = ["Row ID", "Component", "Description"]


def _make_table(row_count: int) -> TableAsset:
    data_rows = [
        [f"ID{n:03d}", f"Component {n}", f"Task {n}"] for n in range(1, row_count + 1)
    ]
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="irrelevant canonical markdown",
        rows=[_TABLE_HEADER, *data_rows],
    )


def _task_response(*titles: str) -> str:
    return json.dumps(
        {
            "confidence_score": 0.9,
            "maintenance_tasks": [
                {"title": title, "source_chunk_id": "chunk_001"} for title in titles
            ],
        }
    )


class _SingleFamilyCandidateSelector:
    def select_for_chunk(self, chunk, **_kwargs):
        return frozenset({ExtractionPromptType.SPECIFICATION})


class _FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now


class _ClockAdvancingLLMService:
    def __init__(self, clock: _FakeClock, seconds_per_call: float, responses: list[str]) -> None:
        self.clock = clock
        self.seconds_per_call = seconds_per_call
        self.responses = list(responses)
        self.calls = 0

    def generate_with_metadata(
        self,
        prompt: str,
        model: str | None = None,
        activity_context=None,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: dict | None = None,
        num_predict: int | None = None,
        num_ctx: int | None = None,
    ) -> LLMGenerationResult:
        self.calls += 1
        self.clock.now += self.seconds_per_call
        return LLMGenerationResult(
            text=self.responses.pop(0), provider_name="fake", finish_reason="stop"
        )


def test_expired_budget_stops_scheduling_new_batches_and_marks_them_unresolved(sample_chunk) -> None:
    chunk_2 = clone_chunk(sample_chunk, chunk_id="chunk_002", content="Second chunk content.")
    clock = _FakeClock()
    llm_service = _ClockAdvancingLLMService(
        clock, seconds_per_call=6.0, responses=[_empty_extraction_response()]
    )
    extraction_service = FakeExtractionService()
    workflow, _validator = make_workflow(
        llm_service,
        extraction_service,
        chunk_batcher=ExtractionChunkBatcher(max_chunks_per_batch=1, max_chars_per_batch=100_000),
        execution_budget_seconds=5.0,
        clock=clock,
    )

    result = workflow.extract("doc_001", [sample_chunk, chunk_2])

    assert llm_service.calls == 1
    assert result.unresolved_chunk_ids == ["chunk_002"]
    assert result.requires_human_review is True
    assert len(extraction_service.saved_results) == 1


def test_unlimited_budget_preserves_existing_successful_extraction_behavior(sample_chunk) -> None:
    chunk_2 = clone_chunk(sample_chunk, chunk_id="chunk_002", content="Second chunk content.")
    clock = _FakeClock()
    llm_service = _ClockAdvancingLLMService(
        clock,
        seconds_per_call=6.0,
        responses=[_empty_extraction_response(), _empty_extraction_response()],
    )
    extraction_service = FakeExtractionService()
    workflow, _validator = make_workflow(
        llm_service,
        extraction_service,
        chunk_batcher=ExtractionChunkBatcher(max_chunks_per_batch=1, max_chars_per_batch=100_000),
        execution_budget_seconds=None,
        clock=clock,
    )

    result = workflow.extract("doc_001", [sample_chunk, chunk_2])

    assert llm_service.calls == 2
    assert result.unresolved_chunk_ids == []
    assert len(extraction_service.saved_results) == 1


def test_multi_family_oversized_table_windowing_respects_the_shared_budget(
    sample_chunk,
) -> None:
    table_chunk = clone_chunk(sample_chunk, chunk_id="chunk_001", content="irrelevant raw content")
    table_chunk.table_ids = ["table_001"]
    table = _make_table(39)
    clock = _FakeClock()
    llm_service = _ClockAdvancingLLMService(
        clock,
        seconds_per_call=3.0,
        responses=[
            _task_response("Task 1"),
            _task_response("Task 11"),
        ],
    )
    extraction_service = FakeExtractionService()
    workflow, _validator = make_workflow(
        llm_service,
        extraction_service,
        execution_strategy=ExtractionExecutionStrategy.MULTI_FAMILY,
        maintenance_table_window_enabled=True,
        maintenance_table_rows_per_window=10,
        execution_budget_seconds=5.0,
        clock=clock,
    )

    result = workflow.extract("doc_001", [table_chunk], tables={"table_001": table})

    assert llm_service.calls == 2
    assert result.unresolved_chunk_ids == ["chunk_001"]
    assert {task.title for task in result.maintenance_tasks} == {"Task 1", "Task 11"}


def test_specialized_family_strategy_stops_candidate_selection_once_budget_is_spent(
    sample_chunk,
) -> None:
    chunk_2 = clone_chunk(sample_chunk, chunk_id="chunk_002", content="Second chunk content.")
    clock = _FakeClock()
    llm_service = _ClockAdvancingLLMService(
        clock, seconds_per_call=6.0, responses=['{"confidence_score": 0.9}']
    )
    extraction_service = FakeExtractionService()
    workflow, _validator = make_workflow(
        llm_service,
        extraction_service,
        chunk_batcher=ExtractionChunkBatcher(max_chunks_per_batch=1, max_chars_per_batch=100_000),
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        candidate_selector=_SingleFamilyCandidateSelector(),
        execution_budget_seconds=5.0,
        clock=clock,
    )

    result = workflow.extract("doc_001", [sample_chunk, chunk_2])

    assert llm_service.calls == 1
    assert result.unresolved_chunk_ids == ["chunk_002"]
    assert result.requires_human_review is True
    assert len(extraction_service.saved_results) == 1
