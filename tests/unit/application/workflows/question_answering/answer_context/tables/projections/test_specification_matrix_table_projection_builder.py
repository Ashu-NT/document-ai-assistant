from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.projections.specification_matrix_table_projection_builder import (
    SpecificationMatrixTableProjectionBuilder,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)


def _make_source() -> AnswerSource:
    return AnswerSource(source_number=1, chunk_id="chunk_1")


def test_project_returns_none_when_table_shape_is_not_specification_matrix() -> None:
    builder = SpecificationMatrixTableProjectionBuilder()
    rows = [["Parameter", "Value"], ["Bore", "25mm"]]

    projection = builder.project(
        source=_make_source(), cleaned_rows=rows, table_shape="record_table"
    )

    assert projection is None


def test_project_returns_none_for_fewer_than_two_rows() -> None:
    builder = SpecificationMatrixTableProjectionBuilder()

    projection = builder.project(
        source=_make_source(),
        cleaned_rows=[["Parameter", "Value"]],
        table_shape="specification_matrix",
    )

    assert projection is None


def test_project_builds_label_value_rows_for_a_simple_matrix() -> None:
    builder = SpecificationMatrixTableProjectionBuilder()
    rows = [
        ["Parameter", "Value"],
        ["Bore", "25mm"],
        ["Voltage", "400V"],
    ]

    projection = builder.project(
        source=_make_source(), cleaned_rows=rows, table_shape="specification_matrix"
    )

    assert projection is not None
    assert isinstance(projection.table_kind, TableQueryStrategy)
    assert projection.table_kind == TableQueryStrategy.SPECIFICATION_MATRIX
    assert projection.headers == ["Label", "Value"]
    assert projection.column_roles == {0: "label", 1: "value"}
    assert projection.body_rows == [["Bore", "25mm"], ["Voltage", "400V"]]


def test_project_combines_value_with_a_separate_unit_column() -> None:
    builder = SpecificationMatrixTableProjectionBuilder()
    rows = [
        ["Parameter", "Value", "Unit"],
        ["Bore", "25", "mm"],
    ]

    projection = builder.project(
        source=_make_source(), cleaned_rows=rows, table_shape="specification_matrix"
    )

    assert projection is not None
    assert projection.body_rows == [["Bore", "25 mm"]]


def test_project_appends_notes_in_parentheses() -> None:
    builder = SpecificationMatrixTableProjectionBuilder()
    rows = [
        ["Parameter", "Value", "Notes"],
        ["Bore", "25mm", "Nominal"],
    ]

    projection = builder.project(
        source=_make_source(), cleaned_rows=rows, table_shape="specification_matrix"
    )

    assert projection is not None
    assert projection.body_rows == [["Bore", "25mm (Nominal)"]]


def test_project_qualifies_labels_with_field_header_for_multi_field_rows() -> None:
    builder = SpecificationMatrixTableProjectionBuilder()
    rows = [
        ["Parameter", "Min", "Max"],
        ["Voltage", "380V", "420V"],
    ]

    projection = builder.project(
        source=_make_source(), cleaned_rows=rows, table_shape="specification_matrix"
    )

    assert projection is not None
    assert projection.body_rows == [
        ["Voltage (Min)", "380V"],
        ["Voltage (Max)", "420V"],
    ]
