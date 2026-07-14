from src.application.workflows.question_answering.answer_context import AnswerSource
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTableProjector,
)


def test_projector_normalizes_shifted_real_world_spare_parts_rows() -> None:
    projector = AnswerTableProjector()
    tables = projector.build(
        [
            AnswerSource(
                source_number=1,
                chunk_id="chunk_spare_real",
                chunk_type="spare_parts_table",
                table_rows=[
                    [
                        "SPARE PARTS LIST",
                        "SPARE PARTS LIST",
                        "SPARE PARTS LIST",
                    ],
                    [
                        "Part Pos. Qty Unit",
                        "Designation Size / Dimension, Material / Surface",
                        "Part No",
                    ],
                    ["0010 1 Pce", "housing", ""],
                    ["", "0115 1 Pce drive shaft", ""],
                    ["P31 1", "Disassembly screw for carrier", "-18/02 2"],
                ],
                metadata={"table_category": "spare_parts_table"},
            )
        ]
    )

    assert len(tables) == 1
    assert tables[0].headers == [
        "Position",
        "Quantity",
        "Unit",
        "Description",
        "Part No.",
        "Service package",
    ]
    assert tables[0].rows[1].cells == ["0115", "1", "Pce", "drive shaft", "", ""]
    assert tables[0].rows[2].cells == [
        "P31",
        "1",
        "",
        "Disassembly screw for carrier",
        "-18/02",
        "2",
    ]


def test_projector_normalizes_split_troubleshooting_rows_into_detail_columns() -> None:
    projector = AnswerTableProjector()
    tables = projector.build(
        [
            AnswerSource(
                source_number=1,
                chunk_id="chunk_trouble_real",
                chunk_type="troubleshooting",
                table_rows=[
                    ["PROBLEM", "PROBABLE CAUSES", "", "POSSIBLE REMEDIES", ""],
                    [
                        "(1) The motor does not start",
                        "1a)",
                        "Motor overload protection cuts in",
                        "1a)",
                        "Check the power supply and make sure that the shaft is free.",
                    ],
                ],
                metadata={"table_category": "troubleshooting_table"},
            )
        ]
    )

    assert len(tables) == 1
    assert tables[0].table_kind == "troubleshooting_table"
    assert tables[0].headers == ["Symptom", "Cause", "Remedy"]
    assert tables[0].rows[0].cells == [
        "(1) The motor does not start",
        "Motor overload protection cuts in",
        "Check the power supply and make sure that the shaft is free.",
    ]
