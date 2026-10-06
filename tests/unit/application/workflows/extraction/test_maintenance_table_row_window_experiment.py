from tests.unit.application.workflows.extraction._test_extraction_workflow_support import *  # noqa: F401,F403

import json

from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.extraction_execution_strategy import (
    ExtractionExecutionStrategy,
)
from src.domain.assets import TableAsset

_HEADER = ["Row ID", "Component", "Description"]


class _FixedFamilyCandidateSelector:
    def __init__(self, families: frozenset) -> None:
        self._families = families

    def select_for_chunk(self, chunk):
        return self._families


def _make_table(row_count: int) -> TableAsset:
    data_rows = [
        [f"ID{n:03d}", f"Component {n}", f"Task {n}"] for n in range(1, row_count + 1)
    ]
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="irrelevant canonical markdown",
        rows=[_HEADER, *data_rows],
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


def _spec_response() -> str:
    return json.dumps(
        {
            "confidence_score": 0.9,
            "specifications": [
                {"parameter": "Tank Capacity", "value": "1200", "unit": "L", "source_chunk_id": "chunk_001"}
            ],
        }
    )


def test_multi_family_execution_is_completely_unaffected_by_windowing_being_enabled(
    sample_chunk,
) -> None:
    table_chunk = clone_chunk(sample_chunk, chunk_id="chunk_001", content="irrelevant raw content")
    table_chunk.table_ids = ["table_001"]
    table = _make_table(39)

    fake_llm_service = FakeLLMService([_empty_extraction_response()])
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        execution_strategy=ExtractionExecutionStrategy.MULTI_FAMILY,
        maintenance_table_window_enabled=True,
        maintenance_table_rows_per_window=10,
    )

    workflow.extract("doc_001", [table_chunk], tables={"table_001": table})

    assert len(fake_llm_service.calls) == 1


def test_specification_sharing_a_batch_with_windowed_maintenance_task_is_unwindowed(
    sample_chunk,
) -> None:
    table_chunk = clone_chunk(sample_chunk, chunk_id="chunk_001", content="irrelevant raw content")
    table_chunk.table_ids = ["table_001"]
    table = _make_table(39)

    # 4 windows of MAINTENANCE_TASK (39 rows / 10 per window) + 1 unwindowed
    # SPECIFICATION call = 5 calls total, in plan order (families sorted
    # alphabetically: maintenance_task < specification).
    fake_llm_service = FakeLLMService(
        [
            _task_response("Task 1"),
            _task_response("Task 11"),
            _task_response("Task 21"),
            _task_response("Task 31"),
            _spec_response(),
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        maintenance_table_window_enabled=True,
        maintenance_table_rows_per_window=10,
        candidate_selector=_FixedFamilyCandidateSelector(
            frozenset(
                {ExtractionPromptType.MAINTENANCE_TASK, ExtractionPromptType.SPECIFICATION}
            )
        ),
    )

    result = workflow.extract("doc_001", [table_chunk], tables={"table_001": table})

    assert len(fake_llm_service.calls) == 5
    assert len(result.specifications) == 1
    assert len(result.maintenance_tasks) == 4


def test_real_merger_combines_distinct_tasks_from_every_window(sample_chunk) -> None:
    table_chunk = clone_chunk(sample_chunk, chunk_id="chunk_001", content="irrelevant raw content")
    table_chunk.table_ids = ["table_001"]
    table = _make_table(39)

    fake_llm_service = FakeLLMService(
        [
            _task_response("Task 1", "Task 2"),
            _task_response("Task 11"),
            _task_response("Task 21"),
            _task_response("Task 31"),
        ]
    )
    fake_extraction_service = FakeExtractionService()
    workflow, _ = make_workflow(
        fake_llm_service,
        fake_extraction_service,
        execution_strategy=ExtractionExecutionStrategy.SPECIALIZED_FAMILY,
        maintenance_table_window_enabled=True,
        maintenance_table_rows_per_window=10,
        candidate_selector=_FixedFamilyCandidateSelector(
            frozenset({ExtractionPromptType.MAINTENANCE_TASK})
        ),
    )

    result = workflow.extract("doc_001", [table_chunk], tables={"table_001": table})

    assert {task.title for task in result.maintenance_tasks} == {
        "Task 1", "Task 2", "Task 11", "Task 21", "Task 31",
    }
    assert len(result.maintenance_tasks) == 5  # no accidental collapsing
