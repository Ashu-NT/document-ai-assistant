from src.application.workflows.question_answering.answer_context import AnswerSource
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTableProjector,
)


def test_projector_detects_key_value_table_headers() -> None:
    projector = AnswerTableProjector()
    tables = projector.build(
        [
            AnswerSource(
                source_number=1,
                chunk_id="chunk_spec",
                chunk_type="technical_specification",
                table_rows=[
                    ["Parameter", "Value"],
                    ["Design pressure", "10 bar"],
                ],
            )
        ]
    )

    assert len(tables) == 1
    assert tables[0].table_kind == "key_value_table"
    assert tables[0].column_roles == {0: "label", 1: "value"}


def test_projector_detects_maintenance_schedule_matrix() -> None:
    projector = AnswerTableProjector()
    tables = projector.build(
        [
            AnswerSource(
                source_number=1,
                chunk_id="chunk_sched",
                chunk_type="maintenance_interval",
                table_rows=[
                    ["Task", "D", "W", "M", "Q", "S", "A"],
                    ["Inspect basket", "", "", "x", "", "x", "x"],
                ],
            )
        ]
    )

    assert len(tables) == 1
    assert tables[0].table_kind == "maintenance_schedule_matrix"


def test_projector_detects_implicit_maintenance_schedule_matrix() -> None:
    projector = AnswerTableProjector()
    tables = projector.build(
        [
            AnswerSource(
                source_number=1,
                chunk_id="chunk_sched",
                chunk_type="maintenance_interval",
                table_rows=[
                    ["D", "Q Q", "M S A", "Task Reference"],
                    ["General Maintenance Work on the Press", "", "", ""],
                    ["X", "", "Check basket for blockages", ""],
                    ["", "X", "Clean dirt from the housing", "See gearbox annex"],
                ],
                metadata={"table_category": "maintenance_interval_table"},
            )
        ]
    )

    assert len(tables) == 1
    assert tables[0].table_kind == "maintenance_schedule_matrix"
    assert tables[0].headers[-2:] == ["Task", "Notes"]
    assert "task" in tables[0].column_roles.values()
    assert "notes" in tables[0].column_roles.values()


def test_projector_deduplicates_same_logical_table_family_and_carries_metadata() -> None:
    projector = AnswerTableProjector()
    tables = projector.build(
        [
            AnswerSource(
                source_number=1,
                chunk_id="chunk_sched_1",
                chunk_type="maintenance_interval",
                table_rows=[
                    ["Task", "Monthly"],
                    ["Inspect basket", "x"],
                ],
                metadata={
                    "logical_table_family_id": "table_family_001",
                    "hydrated_table_ids": "table_001,table_002",
                    "table_category": "maintenance_interval_table",
                    "table_category_confidence": "0.95",
                    "table_row_start": "1",
                    "table_row_end": "2",
                },
            ),
            AnswerSource(
                source_number=2,
                chunk_id="chunk_sched_2",
                chunk_type="maintenance_interval",
                table_rows=[
                    ["Task", "Monthly"],
                    ["Replace gasket", "x"],
                ],
                metadata={
                    "logical_table_family_id": "table_family_001",
                },
            ),
        ]
    )

    assert len(tables) == 1
    assert tables[0].logical_table_family_id == "table_family_001"
    assert tables[0].physical_table_ids == ["table_001", "table_002"]
    assert tables[0].table_category == "maintenance_interval_table"
    assert tables[0].table_category_confidence == 0.95
    assert tables[0].row_start == 1
    assert tables[0].row_end == 2
