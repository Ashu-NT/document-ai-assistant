from src.application.workflows.extraction.response.merging.task_merger import merge_tasks
from src.domain.extraction import ExtractionResult, MaintenanceTask


def _result_with_task(**task_kwargs) -> ExtractionResult:
    task_kwargs.setdefault("task_id", "task_tmp")
    task_kwargs.setdefault("document_id", "doc_001")
    return ExtractionResult(
        extraction_id="ext_1",
        document_id="doc_001",
        maintenance_tasks=[MaintenanceTask(**task_kwargs)],
    )


def test_results_from_every_window_are_accumulated() -> None:
    windows = [
        _result_with_task(task_id=f"task_{i}", title=f"Task {i}", source_chunk_id="chunk_canonical")
        for i in range(4)
    ]

    merged = merge_tasks(windows)

    assert len(merged) == 4
    assert {task.title for task in merged} == {"Task 0", "Task 1", "Task 2", "Task 3"}


def test_distinct_source_rows_with_genuinely_different_titles_are_not_collapsed() -> None:
    """Real MTU table rows WM00084/WM00085/WM00086 (same window, same single
    LLM call, same component category "FUEL SYSTEM (LOW PRESSURE)"), with
    their ORIGINAL distinguishing source text preserved verbatim."""
    wm00084 = _result_with_task(
        title="Fuel prefilter, replace filter",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        source_chunk_id="chunk_canonical",
    )
    wm00085 = _result_with_task(
        title="Additional fuel filter: Replace easy-change fuel filter",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        source_chunk_id="chunk_canonical",
    )
    wm00086 = _result_with_task(
        title="Replace easy-change fuel filter",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        source_chunk_id="chunk_canonical",
    )

    merged = merge_tasks([wm00084, wm00085, wm00086])

    assert len(merged) == 3


def test_known_defect_model_paraphrase_collision_silently_collapses_distinct_tasks() -> None:
    """CONFIRMED DEFECT (not yet fixed - see PHASE 2B merge-integrity audit
    report): in the real live MTU extraction, the model paraphrased
    WM00085's title down to match WM00086's verbatim title, and
    ExtractionResultMerger's (title, interval, component_name) identity key
    has no other signal (no stable table-row/task-code field exists on
    MaintenanceTask) to tell these two genuinely distinct, separately-coded
    maintenance obligations apart once their titles collide post-paraphrase.
    This test pins the CURRENT (defective) behavior as a regression sensor,
    not as an endorsement of it."""
    wm00085_as_actually_paraphrased_by_the_model = _result_with_task(
        title="Replace easy-change fuel filter",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        source_chunk_id="chunk_canonical",
    )
    wm00086 = _result_with_task(
        title="Replace easy-change fuel filter",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        source_chunk_id="chunk_canonical",
    )

    merged = merge_tasks(
        [wm00085_as_actually_paraphrased_by_the_model, wm00086]
    )

    assert len(merged) == 1  # two distinct source rows -> one surviving task


def test_merge_never_silently_overwrites_a_populated_field_with_a_conflicting_value() -> None:
    first = _result_with_task(
        title="Replace filter",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        description="First description",
        source_chunk_id="chunk_a",
    )
    second = _result_with_task(
        title="Replace filter",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        description="Second, different description",
        source_chunk_id="chunk_b",
    )

    merged = merge_tasks([first, second])

    assert len(merged) == 1
    # fill-if-missing only - the first-seen value is kept, never overwritten
    assert merged[0].description == "First description"
    assert merged[0].source_chunk_id == "chunk_a"
