from src.application.workflows.parsing.tables.normalization.key_value.specification_key_value_table_normalizer import (
    SpecificationKeyValueTableNormalizer,
)

_WRAPPED_ROWS = [
    ["Model", "XV2000", "Speed", "1450 RPM"],
    ["Weight", "120 kg", "Diameter", "250 mm"],
]


def test_normalize_projects_wrapped_rows_for_each_applicable_category() -> None:
    for category in (
        "technical_data_table",
        "operating_limits_table",
        "sensor_instrument_table",
        "identifier_table",
        "connection_table",
    ):
        normalized = SpecificationKeyValueTableNormalizer().normalize(
            _WRAPPED_ROWS,
            table_category=category,
            chunk_type=None,
        )
        assert normalized is not None, category
        assert normalized.headers == ["Label", "Value"]


def test_normalize_returns_none_when_explicit_header_already_present() -> None:
    """Parity guard: this exact fixture is asserted elsewhere as an
    untouched-category case for `TableRowSemanticNormalizer` -- confirms
    this normalizer correctly defers rather than over-triggering on
    already-well-formed tables."""
    normalized = SpecificationKeyValueTableNormalizer().normalize(
        [["Parameter", "Value"], ["Voltage", "400V"]],
        table_category="technical_data_table",
        chunk_type=None,
    )

    assert normalized is None


def test_normalize_returns_none_when_header_keyword_accidentally_appears() -> None:
    """Regression guard: 'Voltage' contains the substring 'tag', one of
    `looks_explicit_header_cell`'s keywords -- confirms this is treated as
    an explicit header (correctly deferred) rather than a coincidence bug
    in this normalizer specifically."""
    normalized = SpecificationKeyValueTableNormalizer().normalize(
        [["Model", "XV2000", "Voltage", "400V"], ["Weight", "120 kg", "Power", "5.5 kW"]],
        table_category="technical_data_table",
        chunk_type=None,
    )

    assert normalized is None


def test_normalize_returns_none_for_a_real_four_column_record_table() -> None:
    # Regression guard for a real bug: this exact table (a real document's
    # material/recycling table) has a genuine 4-column header, but none of
    # its header words were in the explicit-header keyword list, so
    # `has_explicit_header_row` returned False and the table fell through
    # into key-value-pair reshaping -- the header row itself got split into
    # two bogus "Label=Value" pairs, and each real 4-attribute record was
    # split into two disconnected, mismatched pairs.
    normalized = SpecificationKeyValueTableNormalizer().normalize(
        [
            ["Material", "Life cycle", "Component", "Recycling"],
            ["Battery", "Maintenance, Disassembly", "Control unit", "Special waste"],
            [
                "Electronics",
                "Disassembly",
                "Control unit, Control cabinet Drive",
                "Electronic waste",
            ],
            ["Metal", "Disassembly", "Guides, Door drive", "Metal waste"],
        ],
        table_category="technical_data_table",
        chunk_type=None,
    )

    assert normalized is None


def test_normalize_returns_none_for_unrelated_category() -> None:
    normalized = SpecificationKeyValueTableNormalizer().normalize(
        _WRAPPED_ROWS,
        table_category="troubleshooting_table",
        chunk_type=None,
    )

    assert normalized is None
