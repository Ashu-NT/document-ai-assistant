from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.workflows.question_answering.answer_context.maintenance.maintenance_task_extractor import (
    MaintenanceTaskExtractor,
)
from src.application.workflows.question_answering.answer_context import (
    AnswerSource,
)


def _make_source(*, content: str = "", table_rows: list[list[str]] | None = None) -> AnswerSource:
    return AnswerSource(
        source_number=1,
        chunk_id="chunk_001",
        content=content,
        table_rows=table_rows,
    )


def test_extract_maintenance_entries_from_structured_rows_with_header() -> None:
    extractor = MaintenanceTaskExtractor()
    source = _make_source(
        table_rows=[
            ["Task", "Interval", "Component"],
            ["Replace filter", "Every 500 hours", "Hydraulic pump"],
        ],
    )

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert len(entries) == 1
    assert entries[0].task == "Replace filter"
    assert entries[0].interval == "Every 500 hours"
    assert entries[0].component == "Hydraulic pump"


def test_extract_maintenance_entries_from_rows_without_header() -> None:
    extractor = MaintenanceTaskExtractor()
    source = _make_source(
        table_rows=[["Inspect gasket every 6 months", "See manual"]],
    )

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert len(entries) == 1
    assert "Inspect gasket" in entries[0].task


def test_extract_maintenance_entries_deduplicates_rows_and_content_matches() -> None:
    extractor = MaintenanceTaskExtractor()
    content = "| Task | Interval |\n|---|---|\n| Replace filter | Every 500 hours |"
    source = _make_source(
        content=content,
        table_rows=[["Task", "Interval"], ["Replace filter", "Every 500 hours"]],
    )

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert len(entries) == 1


def test_extract_maintenance_entries_ignores_table_rows_when_absent() -> None:
    extractor = MaintenanceTaskExtractor()
    source = _make_source(content="No maintenance content here.")

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert entries == []


def test_extract_maintenance_entries_from_schedule_matrix() -> None:
    extractor = MaintenanceTaskExtractor()
    source = _make_source(
        table_rows=[
            ["Task", "D", "W", "M", "Q", "S", "A"],
            ["Inspect basket", "", "", "x", "", "x", "x"],
        ]
    )

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert len(entries) == 1
    assert entries[0].task == "Inspect basket"
    assert entries[0].interval == "Monthly; Semi-Annual; Annual"


def test_extract_maintenance_entries_from_schedule_matrix_cleans_schedule_prefix() -> None:
    extractor = MaintenanceTaskExtractor()
    source = _make_source(
        table_rows=[
            ["Task", "D", "M", "S", "A"],
            ["M S A=Check gearbox for leaks", "x", "", "x", "x"],
        ]
    )

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert len(entries) == 1
    assert entries[0].task == "Check gearbox for leaks"
    assert entries[0].interval == "Daily; Semi-Annual; Annual"


def test_extract_maintenance_entries_from_implicit_schedule_matrix() -> None:
    extractor = MaintenanceTaskExtractor()
    source = _make_source(
        table_rows=[
            ["D", "Q Q", "M S A", "Task Reference"],
            ["General Maintenance Work on the Press", "", "", ""],
            ["X", "", "Check basket for blockages", ""],
            ["", "X", "Clean dirt from the housing", "See gearbox annex"],
            ["X", "", "M S A=Check that the screw runs evenly in the basket", ""],
        ],
    )
    source.chunk_type = "maintenance_interval"
    source.metadata = {"table_category": "maintenance_interval_table"}

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert len(entries) == 3
    assert entries[0].task == "Check basket for blockages"
    assert entries[0].interval == "Daily"
    assert entries[1].task == "Clean dirt from the housing"
    assert entries[1].interval == "Quarterly"
    assert entries[1].notes == "See gearbox annex"
    assert entries[2].task == "Check that the screw runs evenly in the basket"
    assert entries[2].interval == "Daily"
    assert entries[2].component is None


def test_extract_maintenance_entries_from_collapsed_compact_schedule_rows() -> None:
    extractor = MaintenanceTaskExtractor()
    source = _make_source(
        table_rows=[
            ["D", "Q Q", "M S A", "Task Reference"],
            ["General Maintenance Work on the Press"],
            ["X", "General visual inspection daily or after period of particularly high load"],
            ["X", "Check basket for fat, fibre growth or blockages & clogging"],
            ["", "X", "Clean dirt from the housing", "See gearbox Annex"],
        ],
    )
    source.chunk_type = "maintenance_interval"
    source.metadata = {"table_category": "maintenance_interval_table"}

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert len(entries) == 3
    assert entries[0].task == "General visual inspection daily or after period of particularly high load"
    assert entries[0].interval == "Daily"
    assert entries[1].task == "Check basket for fat, fibre growth or blockages & clogging"
    assert entries[1].interval == "Daily"
    assert entries[2].task == "Clean dirt from the housing"
    assert entries[2].interval == "Quarterly"
    assert entries[2].notes == "See gearbox Annex"
