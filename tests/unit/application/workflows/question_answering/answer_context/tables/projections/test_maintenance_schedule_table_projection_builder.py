from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.projections.maintenance_schedule_table_projection_builder import (
    MaintenanceScheduleTableProjectionBuilder,
)


def _make_source(**overrides: object) -> AnswerSource:
    defaults: dict = {
        "source_number": 1,
        "chunk_id": "chunk_1",
        "chunk_type": "maintenance_interval",
    }
    defaults.update(overrides)
    return AnswerSource(**defaults)


def test_project_returns_none_for_fewer_than_two_rows() -> None:
    builder = MaintenanceScheduleTableProjectionBuilder()

    projection = builder.project(
        source=_make_source(),
        cleaned_rows=[["Task", "D"]],
        table_category=None,
        table_shape=None,
    )

    assert projection is None


def test_project_returns_none_when_not_a_maintenance_schedule_table() -> None:
    builder = MaintenanceScheduleTableProjectionBuilder()
    rows = [
        ["Fault", "Cause", "Remedy"],
        ["No power", "Blown fuse", "Replace fuse"],
    ]

    projection = builder.project(
        source=_make_source(chunk_type=None),
        cleaned_rows=rows,
        table_category=None,
        table_shape="record_table",
    )

    assert projection is None


def test_project_builds_task_interval_and_notes_columns_and_drops_blank_rows() -> None:
    builder = MaintenanceScheduleTableProjectionBuilder()
    rows = [
        ["Task", "D", "W", "M", "Notes"],
        ["Inspect basket", "", "", "x", "Check for debris"],
        ["Replace gasket", "x", "", "", ""],
        ["", "", "", "", ""],
    ]

    projection = builder.project(
        source=_make_source(),
        cleaned_rows=rows,
        table_category=None,
        table_shape=None,
    )

    assert projection is not None
    assert projection.table_kind == "maintenance_schedule_matrix"
    assert projection.headers == ["Task", "Interval", "Component", "Notes"]
    assert projection.column_roles == {0: "task", 1: "interval", 2: "component", 3: "notes"}
    assert projection.body_rows == [
        ["Inspect basket", "Monthly", "", "Check for debris"],
        ["Replace gasket", "Daily", "", ""],
    ]


def test_project_resolves_component_column_when_present() -> None:
    builder = MaintenanceScheduleTableProjectionBuilder()
    rows = [
        ["Task", "Component", "D", "W"],
        ["Inspect", "Main pump", "x", ""],
    ]

    projection = builder.project(
        source=_make_source(),
        cleaned_rows=rows,
        table_category=None,
        table_shape=None,
    )

    assert projection is not None
    assert projection.body_rows == [["Inspect", "Daily", "Main pump", ""]]
