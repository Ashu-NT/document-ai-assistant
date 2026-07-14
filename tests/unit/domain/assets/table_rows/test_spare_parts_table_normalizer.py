from src.domain.assets.table_rows.spare_parts_table_normalizer import (
    SparePartsTableNormalizer,
)


def test_normalizes_shifted_spare_parts_rows_with_embedded_position_tokens() -> None:
    normalized = SparePartsTableNormalizer().normalize(
        [
            [
                "SPARE PARTS LIST",
                "SPARE PARTS LIST",
                "SPARE PARTS LIST",
                "SPARE PARTS LIST",
            ],
            [
                "Part Pos. Qty Unit",
                "Designation Size / Dimension, Material / Surface",
                "Part No",
                "",
            ],
            ["0010 1 Pce", "housing", "", ""],
            ["0020 4 Pce pin", "", "", ""],
            ["0110 1 Pce", "drive shaft", "", ""],
            ["", "0115 1 Pce drive shaft", "", ""],
            ["", "0120 2 Pce wheel", "", ""],
            ["P31 1", "Disassembly screw for carrier", "-18/02 2", ""],
        ],
        table_category="spare_parts_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == [
        "Position",
        "Quantity",
        "Unit",
        "Description",
        "Part No.",
        "Service package",
    ]
    assert normalized.rows[0] == ["0010", "1", "Pce", "housing", "", ""]
    assert normalized.rows[3] == ["0115", "1", "Pce", "drive shaft", "", ""]
    assert normalized.rows[5] == [
        "P31",
        "1",
        "",
        "Disassembly screw for carrier",
        "-18/02",
        "2",
    ]


def test_normalizes_rows_when_unit_is_split_into_the_next_column() -> None:
    normalized = SparePartsTableNormalizer().normalize(
        [
            ["SPARE PARTS LIST", "SPARE PARTS LIST", "SPARE PARTS LIST"],
            ["Part Pos.", "Qty Unit", "Designation"],
            ["5040 4", "Pce", "spring washer"],
            ["7000 2", "Pce", "seal housing"],
        ],
        table_category="spare_parts_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Position", "Quantity", "Unit", "Description"]
    assert normalized.rows == [
        ["5040", "4", "Pce", "spring washer"],
        ["7000", "2", "Pce", "seal housing"],
    ]
