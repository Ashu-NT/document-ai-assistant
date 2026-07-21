from src.application.workflows.question_answering.answer_context.maintenance.maintenance_entry_merger import (
    MaintenanceEntryMerger,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerMaintenanceEntry,
)


def _make_entry(
    *,
    task: str,
    interval: str,
    component: str | None = None,
    source_number: int = 1,
) -> AnswerMaintenanceEntry:
    return AnswerMaintenanceEntry(
        task=task,
        interval=interval,
        component=component,
        notes=None,
        source_number=source_number,
    )


def test_merge_combines_entries_with_identical_task_and_interval() -> None:
    merger = MaintenanceEntryMerger()
    entries = [
        _make_entry(task="Replace filter", interval="Every 500 hours", source_number=1),
        _make_entry(task="Replace filter", interval="Every 500 hours", source_number=2),
    ]

    merged = merger.merge(entries)

    assert len(merged) == 1
    assert merged[0].source_numbers == [1, 2]


def test_merge_combines_entries_with_substring_task_match() -> None:
    merger = MaintenanceEntryMerger()
    entries = [
        _make_entry(task="Replace filter", interval="Every 500 hours"),
        _make_entry(task="Replace filter element", interval="Every 500 hours"),
    ]

    merged = merger.merge(entries)

    assert len(merged) == 1
    assert merged[0].task == "Replace filter element"


def test_merge_combines_entries_with_similar_component_when_task_differs() -> None:
    merger = MaintenanceEntryMerger()
    entries = [
        _make_entry(
            task="Inspect condition",
            interval="Every 500 hours",
            component="hydraulic pump assembly",
        ),
        _make_entry(
            task="Inspect wear",
            interval="Every 500 hours",
            component="hydraulic pump assembly unit",
        ),
    ]

    merged = merger.merge(entries)

    assert len(merged) == 1


def test_merge_keeps_entries_with_different_intervals_separate() -> None:
    merger = MaintenanceEntryMerger()
    entries = [
        _make_entry(task="Replace filter", interval="Every 500 hours"),
        _make_entry(task="Replace filter", interval="Every 1000 hours"),
    ]

    merged = merger.merge(entries)

    assert len(merged) == 2


def test_merge_absorbs_not_specified_duplicate_into_interval_entry() -> None:
    merger = MaintenanceEntryMerger()
    entries = [
        _make_entry(task="Check gearbox for leaks", interval="Not specified"),
        _make_entry(
            task="M S A=Check gearbox for leaks",
            interval="Monthly; Semi-Annual; Annual",
        ),
    ]

    merged = merger.merge(entries)

    assert len(merged) == 1
    assert merged[0].interval == "Monthly; Semi-Annual; Annual"


def test_merge_keeps_entries_with_different_leading_action_separate() -> None:
    merger = MaintenanceEntryMerger()
    entries = [
        _make_entry(task="Replace filter", interval="Every 500 hours"),
        _make_entry(task="Inspect filter", interval="Every 500 hours"),
    ]

    merged = merger.merge(entries)

    assert len(merged) == 2


def test_merge_preserves_original_first_appearance_order_across_buckets() -> None:
    """Bucketing by (interval, action) internally must not reorder the
    output relative to the order entries were first seen in the input."""
    merger = MaintenanceEntryMerger()
    entries = [
        _make_entry(task="Replace filter", interval="Every 500 hours", source_number=1),
        _make_entry(task="Inspect gasket", interval="Every 1000 hours", source_number=2),
        _make_entry(task="Replace filter", interval="Every 500 hours", source_number=3),
        _make_entry(task="Lubricate bearing", interval="Every 250 hours", source_number=4),
    ]

    merged = merger.merge(entries)

    assert [entry.task for entry in merged] == [
        "Replace filter",
        "Inspect gasket",
        "Lubricate bearing",
    ]
    assert merged[0].source_numbers == [1, 3]


def test_merge_returns_empty_list_for_empty_input() -> None:
    assert MaintenanceEntryMerger().merge([]) == []
