from src.domain.assets.table_rows.troubleshooting_table_normalizer import (
    TroubleshootingTableNormalizer,
)


def test_normalizes_standard_symptom_cause_remedy_table() -> None:
    normalized = TroubleshootingTableNormalizer().normalize(
        [
            ["Symptom", "Cause", "Remedy"],
            ["Pump does not start", "No power supply", "Check main breaker"],
            ["Excessive noise", "Worn bearing", "Replace bearing"],
        ],
        table_category="troubleshooting_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Symptom", "Cause", "Remedy"]
    assert normalized.rows == [
        ["Pump does not start", "No power supply", "Check main breaker"],
        ["Excessive noise", "Worn bearing", "Replace bearing"],
    ]


def test_maps_synonym_headers_to_the_canonical_fields() -> None:
    normalized = TroubleshootingTableNormalizer().normalize(
        [
            ["Problem", "Possible Cause", "Solution"],
            ["Motor overheats", "Blocked ventilation", "Clean vents"],
        ],
        table_category="troubleshooting_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Symptom", "Cause", "Remedy"]


def test_does_not_normalize_when_neither_category_nor_chunk_type_matches() -> None:
    normalized = TroubleshootingTableNormalizer().normalize(
        [
            ["Symptom", "Cause", "Remedy"],
            ["Pump does not start", "No power supply", "Check main breaker"],
        ],
        table_category="technical_data_table",
        chunk_type="technical_specification",
    )

    assert normalized is None


def test_does_not_map_a_header_via_a_substring_inside_an_unrelated_word() -> None:
    """Regression test: "Reaction" contains the "action" marker as a bare
    substring but is not itself a remedy/action column - word-boundary
    matching must not conflate the two.
    """
    normalized = TroubleshootingTableNormalizer().normalize(
        [
            ["Symptom", "Cause", "Reaction"],
            ["Valve stuck", "Debris in seat", "Flush the line"],
        ],
        table_category="troubleshooting_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Symptom", "Cause"]


def test_maps_a_pluralized_header_to_its_singular_marker() -> None:
    """Regression test: word-boundary marker matching must still accept
    the regular plural real headers commonly use ("Probable Causes"),
    not just the exact singular marker text.
    """
    normalized = TroubleshootingTableNormalizer().normalize(
        [
            ["Problem", "Probable Causes", "Corrective Actions"],
            ["Motor overheats", "Blocked ventilation", "Clean vents"],
        ],
        table_category="troubleshooting_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Symptom", "Cause", "Remedy"]


def test_realigns_a_merged_header_that_landed_on_its_numbering_sub_column() -> None:
    """Regression test, grounded in a real ingested document: a header
    like "PROBABLE CAUSES" can visually span a "1a) <text>" sub-column
    pair but land its label on the bare numbering sub-column only,
    leaving the actual cause/remedy text one column over, unlabeled.
    The real content must still be recovered, not the numbering token.
    """
    normalized = TroubleshootingTableNormalizer().normalize(
        [
            ["PROBLEM", "PROBABLE CAUSES", "", "POSSIBLE REMEDIES", ""],
            [
                "(1) The motor does not start",
                "1a)",
                "Motor overload protection cuts in",
                "1a)",
                "Check the power supply.",
            ],
            [
                "(1) The motor does not start",
                "1b)",
                "Shaft locked",
                "1b)",
                "Remove the cause of lockage.",
            ],
        ],
        table_category="troubleshooting_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Symptom", "Cause", "Remedy"]
    assert normalized.rows == [
        [
            "(1) The motor does not start",
            "Motor overload protection cuts in",
            "Check the power supply.",
        ],
        [
            "(1) The motor does not start",
            "Shaft locked",
            "Remove the cause of lockage.",
        ],
    ]


def test_drops_rows_with_no_symptom_cause_or_remedy_signal() -> None:
    normalized = TroubleshootingTableNormalizer().normalize(
        [
            ["Symptom", "Cause", "Remedy", "Notes"],
            ["", "", "", "See appendix B"],
            ["Leaking seal", "Wear", "Replace seal", ""],
        ],
        table_category="troubleshooting_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.rows == [["Leaking seal", "Wear", "Replace seal", ""]]


def test_prefers_descriptive_troubleshooting_cells_over_enumerator_markers() -> None:
    normalized = TroubleshootingTableNormalizer().normalize(
        [
            ["PROBLEM", "PROBABLE CAUSES", "", "POSSIBLE REMEDIES", ""],
            [
                "(1) The motor does not start",
                "1a)",
                "Motor overload protection cuts in",
                "1a)",
                "Check the power supply and make sure that the shaft is free.",
            ],
        ],
        table_category="troubleshooting_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Symptom", "Cause", "Remedy"]
    assert normalized.rows == [
        [
            "(1) The motor does not start",
            "Motor overload protection cuts in",
            "Check the power supply and make sure that the shaft is free.",
        ]
    ]
