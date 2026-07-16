from src.application.workflows.question_answering.answer_context.tables.answer_table_schema_inferer import (
    AnswerTableSchemaInferer,
)


def test_infer_detects_maintenance_schedule_matrix_from_headers() -> None:
    kind, roles = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=["Task", "Daily", "Weekly"],
        rows=[["Inspect filter", "x", ""]],
    )

    assert kind == "maintenance_schedule_matrix"
    assert roles[0] == "task"


def test_infer_detects_key_value_table_from_headers() -> None:
    kind, _ = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=["Label", "Value"],
    )

    assert kind == "key_value_table"


def test_infer_detects_specification_matrix_from_table_shape() -> None:
    kind, _ = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=["Voltage", "400V"],
        table_shape="specification_matrix",
    )

    assert kind == "specification_matrix"


def test_infer_detects_troubleshooting_table_from_category() -> None:
    kind, _ = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=["Symptom", "Cause", "Remedy"],
        table_category="troubleshooting_table",
    )

    assert kind == "troubleshooting_table"


def test_infer_collapses_record_style_categories_to_record_table() -> None:
    for category in (
        "technical_data_table",
        "operating_limits_table",
        "connection_table",
        "identifier_table",
        "operation_reference_table",
        "sensor_instrument_table",
        "spare_parts_table",
        "certification_table",
    ):
        kind, _ = AnswerTableSchemaInferer().infer(
            chunk_type=None,
            headers=["A", "B"],
            table_category=category,
        )
        assert kind == "record_table", category


def test_infer_falls_back_to_record_table_for_technical_specification_chunk_type() -> None:
    kind, _ = AnswerTableSchemaInferer().infer(
        chunk_type="technical_specification",
        headers=["A", "B"],
    )

    assert kind == "record_table"


def test_infer_returns_general_table_when_nothing_matches() -> None:
    kind, _ = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=["A", "B"],
    )

    assert kind == "general_table"


def test_infer_now_covers_toc_table_category() -> None:
    """Newly-covered by the shared resolution core -- previously fell
    through to general_table by omission, same output today, but now a
    considered decision shared with the prompt path."""
    kind, _ = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=["Number", "Title", "Page"],
        table_category="toc_table",
    )

    assert kind == "general_table"


def test_infer_now_covers_maintenance_interval_table_category() -> None:
    """This is the confirmed real divergence the unification fixes: the
    prompt path already classified this category as a maintenance table;
    the answer path previously fell through to general_table."""
    kind, _ = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=["Component", "Notes"],
        table_category="maintenance_interval_table",
    )

    assert kind == "maintenance_schedule_table"


def test_infer_now_covers_performance_curve_matrix_shape() -> None:
    kind, _ = AnswerTableSchemaInferer().infer(
        chunk_type=None,
        headers=["RPM", "Flow", "Head"],
        table_shape="performance_curve_matrix",
    )

    assert kind == "general_table"
