from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.workflows.question_answering.answer_context.key_value_extractor import (
    KeyValueExtractor,
)
from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerSource,
)


def _make_source(*, content: str = "", table_rows: list[list[str]] | None = None) -> AnswerSource:
    return AnswerSource(
        source_number=1,
        chunk_id="chunk_001",
        content=content,
        table_rows=table_rows,
    )


def test_extract_finds_key_values_from_structured_rows() -> None:
    extractor = KeyValueExtractor()
    source = _make_source(
        content="",
        table_rows=[["Parameter", "Value"], ["Design pressure", "10 bar"]],
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    )

    assert len(key_values) == 1
    assert key_values[0].key == "Design pressure"
    assert key_values[0].value == "10 bar"


def test_extract_does_not_duplicate_when_rows_and_content_agree() -> None:
    extractor = KeyValueExtractor()
    content = "| Design pressure | 10 bar |"
    source = _make_source(
        content=content,
        table_rows=[["Design pressure", "10 bar"]],
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    )

    assert len(key_values) == 1


def test_extract_ignores_table_rows_for_unsupported_intent() -> None:
    extractor = KeyValueExtractor()
    source = _make_source(
        table_rows=[["Design pressure", "10 bar"]],
    )

    key_values = extractor.extract(
        [source],
        answer_intent=AnswerIntent.PROCEDURE_STEPS,
    )

    assert key_values == []


def test_extract_maintenance_entries_from_structured_rows_with_header() -> None:
    extractor = KeyValueExtractor()
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
    extractor = KeyValueExtractor()
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
    extractor = KeyValueExtractor()
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
    extractor = KeyValueExtractor()
    source = _make_source(content="No maintenance content here.")

    entries = extractor.extract_maintenance_entries(
        [source],
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )

    assert entries == []
