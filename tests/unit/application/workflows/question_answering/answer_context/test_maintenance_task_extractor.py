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
