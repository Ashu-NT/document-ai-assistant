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
