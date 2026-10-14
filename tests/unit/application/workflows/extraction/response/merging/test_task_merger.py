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


def test_without_a_verified_task_code_identical_paraphrased_titles_still_collapse() -> None:
    """Documents the PRESERVED fallback behavior (title/interval/component
    key only) whenever no verified task_code is available on either side -
    e.g. a non-windowed extraction path, or a code that failed grounding.
    This is a known, accepted limitation of the fallback path, not the
    fixed path (see test_verified_task_codes_prevent_the_paraphrase_collision
    below for the actual fix)."""
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

    assert len(merged) == 1


def test_verified_task_codes_prevent_the_paraphrase_collision() -> None:
    """THE FIX: same two rows, same collided title, but now with their
    verified task_code attached (as MaintenanceTaskBuilder now produces) -
    the two distinct source rows must both survive."""
    wm00085 = _result_with_task(
        title="Replace easy-change fuel filter",
        task_code="WM00085",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        source_chunk_id="chunk_canonical",
    )
    wm00086 = _result_with_task(
        title="Replace easy-change fuel filter",
        task_code="WM00086",
        component_name="FUEL SYSTEM (LOW PRESSURE)",
        source_chunk_id="chunk_canonical",
    )

    merged = merge_tasks([wm00085, wm00086])

    assert len(merged) == 2
    assert {task.task_code for task in merged} == {"WM00085", "WM00086"}


def test_same_verified_task_code_from_overlapping_windows_merges() -> None:
    first_window = _result_with_task(
        title="Check engine oil level", task_code="WM00285", source_chunk_id="chunk_canonical",
    )
    second_window_duplicate = _result_with_task(
        title="Check engine oil level", task_code="WM00285", source_chunk_id="chunk_canonical",
    )

    merged = merge_tasks([first_window, second_window_duplicate])

    assert len(merged) == 1
    assert merged[0].task_code == "WM00285"


def test_identical_task_codes_in_different_documents_are_not_merged() -> None:
    doc_a = _result_with_task(
        document_id="doc_a", title="Replace filter", task_code="WM00085",
        source_chunk_id="chunk_a",
    )
    doc_b = _result_with_task(
        document_id="doc_b", title="Replace filter", task_code="WM00085",
        source_chunk_id="chunk_b",
    )

    merged = merge_tasks([doc_a, doc_b])

    assert len(merged) == 2


def test_multiple_obligations_from_one_source_row_stay_distinguishable() -> None:
    """Same verified task_code (one source row), but two genuinely
    different obligations described in that row's text - must not
    collapse into one just because they share a code."""
    obligation_one = _result_with_task(
        title="Check valve clearance", task_code="WM00094", source_chunk_id="chunk_canonical",
    )
    obligation_two = _result_with_task(
        title="Adjust valve clearance as necessary", task_code="WM00094",
        source_chunk_id="chunk_canonical",
    )

    merged = merge_tasks([obligation_one, obligation_two])

    assert len(merged) == 2


def test_source_evidence_is_preserved_through_a_merge() -> None:
    first = _result_with_task(
        title="Check engine oil level", task_code="WM00285", source_chunk_id="chunk_canonical",
    )
    duplicate_from_another_batch = _result_with_task(
        title="Check engine oil level", task_code="WM00285", source_chunk_id="chunk_canonical",
    )

    merged = merge_tasks([first, duplicate_from_another_batch])

    assert len(merged) == 1
    assert merged[0].source_chunk_id == "chunk_canonical"


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
