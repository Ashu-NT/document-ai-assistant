from src.application.workflows.question_answering.answer_context import AnswerSource
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTableProjector,
)


def test_projector_normalizes_headerless_key_value_rows() -> None:
    projector = AnswerTableProjector()
    tables = projector.build(
        [
            AnswerSource(
                source_number=1,
                chunk_id="chunk_spec",
                chunk_type="technical_specification",
                table_rows=[
                    ["Tank Capacity", "1,200 L"],
                    ["Pump Capacity", "16,000 L/hr"],
                ],
            )
        ]
    )

    assert len(tables) == 1
    assert tables[0].table_kind == "key_value_table"
    assert tables[0].headers == ["Label", "Value"]
    assert tables[0].rows[0].cells == ["Tank Capacity", "1,200 L"]
