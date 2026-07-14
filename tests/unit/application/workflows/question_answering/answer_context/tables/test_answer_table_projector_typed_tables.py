from src.application.workflows.question_answering.answer_context import AnswerSource
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTableProjector,
)


def test_projector_normalizes_troubleshooting_tables_into_typed_answer_tables() -> None:
    projector = AnswerTableProjector()
    tables = projector.build(
        [
            AnswerSource(
                source_number=1,
                chunk_id="chunk_troubleshooting",
                chunk_type="troubleshooting",
                table_rows=[
                    ["Symptom", "Probable cause", "Remedy", "Comments"],
                    [
                        "Pump does not start",
                        "No power supply",
                        "Check fuse",
                        "Verify breaker",
                    ],
                ],
                metadata={"table_category": "troubleshooting_table"},
            )
        ]
    )

    assert len(tables) == 1
    assert tables[0].table_kind == "troubleshooting_table"
    assert tables[0].headers == ["Symptom", "Cause", "Remedy", "Notes"]
    assert tables[0].column_roles == {
        0: "symptom",
        1: "cause",
        2: "remedy",
        3: "notes",
    }
    assert tables[0].rows[0].cells == [
        "Pump does not start",
        "No power supply",
        "Check fuse",
        "Verify breaker",
    ]
