from src.application.workflows.parsing.tables.normalization.spare_parts_table_normalizer import (
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


def test_normalizes_a_cleanly_columnar_table_and_recovers_the_trailing_part_number() -> None:
    """Regression test: when Docling cell matching works correctly and a
    spare-parts table is already split into separate columns (the more
    common real-world layout, as opposed to the merged-cell shift cases
    above), the trailing Part No. cell must not be silently absorbed
    into Description.
    """
    normalized = SparePartsTableNormalizer().normalize(
        [
            ["Pos", "Qty", "Unit", "Description", "Part No"],
            ["10", "2", "Pce", "Hex bolt M8x20", "900.123.456"],
            ["20", "1", "Pce", "Washer", "900.789.012"],
        ],
        table_category="spare_parts_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.rows == [
        ["2", "Pce", "Hex bolt M8x20", "900.123.456", "10"],
        ["1", "Pce", "Washer", "900.789.012", "20"],
    ]


def test_normalizes_a_plain_reference_to_code_lookup_table_with_no_position_or_quantity() -> None:
    """Regression test grounded in a real ingested document: a simple
    parts-reference table headed "Reference | Code" has no position or
    quantity concept at all - every existing row-parsing strategy
    required a position+quantity-led row, so this whole shape used to
    fail to normalize entirely.
    """
    normalized = SparePartsTableNormalizer().normalize(
        [
            ["REFERENCE", "CODE"],
            [
                "LP PUMP MXVL25-220C SST 316L DN25 400/3/50 (THREADED PORTS)",
                "1514101",
            ],
            ["HP PIPE PA-SR-P03", "0327243"],
        ],
        table_category="spare_parts_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Description", "Part No."]
    assert normalized.rows == [
        [
            "LP PUMP MXVL25-220C SST 316L DN25 400/3/50 (THREADED PORTS)",
            "1514101",
        ],
        ["HP PIPE PA-SR-P03", "0327243"],
    ]


def test_does_not_misread_a_data_row_ending_in_a_header_like_word_as_a_header() -> None:
    """Regression test: `looks_explicit_header_cell` matches several
    short, generic keywords ("pin", "wire", "tag", ...) that are also
    common trailing words in genuine part descriptions (e.g. "0020 4 Pce
    pin"). A data row must not be silently dropped just because it ends
    in one of these words - a real position+quantity seed always wins.
    """
    normalized = SparePartsTableNormalizer().normalize(
        [
            ["Part Pos. Qty Unit", "Designation", "Part No", ""],
            ["0010 1 Pce", "housing", "", ""],
            ["0020 4 Pce pin", "", "", ""],
        ],
        table_category="spare_parts_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert len(normalized.rows) == 2
    assert normalized.rows[1][0] == "0020"
