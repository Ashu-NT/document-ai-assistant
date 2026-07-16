from src.application.workflows.question_answering.answer_context.maintenance.maintenance_candidate_parser import (
    parse_table_header,
)


def test_parse_table_header_recognizes_baseline_roles() -> None:
    assert parse_table_header(["Task", "Interval", "Component", "Notes"]) == [
        "task",
        "interval",
        "component",
        "notes",
    ]


def test_parse_table_header_recognizes_previously_missing_task_alias() -> None:
    """Regression test: "Inspection Item" is a real header-alias gap that
    the general-purpose table-header classifier already recognized as a
    task-role alias, but this maintenance-specific parser's own copy did
    not."""
    assert parse_table_header(["Inspection Item", "Interval"]) == [
        "task",
        "interval",
    ]


def test_parse_table_header_recognizes_previously_missing_interval_aliases() -> None:
    assert parse_table_header(["Task", "Inspection Interval"]) == [
        "task",
        "interval",
    ]
    assert parse_table_header(["Task", "Service Interval"]) == [
        "task",
        "interval",
    ]


def test_parse_table_header_recognizes_previously_missing_notes_aliases() -> None:
    assert parse_table_header(["Task", "Note"]) == ["task", "notes"]
    assert parse_table_header(["Task", "Reference"]) == ["task", "notes"]


def test_parse_table_header_returns_none_without_a_task_column() -> None:
    assert parse_table_header(["Interval", "Component"]) is None


def test_parse_table_header_returns_none_when_any_cell_is_unrecognized() -> None:
    assert parse_table_header(["Task", "Unrecognizable Header"]) is None
