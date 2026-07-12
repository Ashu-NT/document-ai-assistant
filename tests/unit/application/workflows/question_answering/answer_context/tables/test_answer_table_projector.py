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
