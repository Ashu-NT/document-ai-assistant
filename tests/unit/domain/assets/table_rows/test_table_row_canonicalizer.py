from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)


def test_canonicalize_promotes_second_row_when_first_row_is_umbrella_header() -> None:
    rows = [
        ["Position 3 (Output)", "Position 3 (Output)"],
        ["Selected option", "Description"],
        ["2", "4-20 mA HART"],
        ["3", "PROFIBUS PA"],
    ]

    canonicalized = TableRowCanonicalizer().canonicalize(rows)

    assert canonicalized == [
        ["Selected option", "Description"],
        ["2", "4-20 mA HART"],
        ["3", "PROFIBUS PA"],
    ]


def test_canonicalize_keeps_a_distinct_banner_row_instead_of_discarding_it() -> None:
    # Regression guard for a real bug: unlike a pure repeated-text umbrella
    # banner ("Position 3 (Output)" | "Position 3 (Output)", fully
    # redundant and safe to discard), a banner row with 2 DIFFERENT texts
    # neither of which looks like a real header (e.g. "Maintenance" | "Fire
    # Sliding Door A-60, door type A3000...") carries real information --
    # which asset this table covers -- that may not appear anywhere else in
    # the document. It must be kept as an ordinary body row under the real
    # header (row 1: "Maintenance Description | Frequency | Interval
    # Period"), not silently deleted the way the pure umbrella case is.
    rows = [
        [
            "Maintenance",
            "Fire Sliding Door A-60, door type A3000 with drive type E3000mini",
            "",
            "",
        ],
        ["Maintenance Description", "", "Frequency", "Interval Period"],
        ["CHECK FIRE SLIDING DOOR A - 60", "", "1", "2 WEEKS"],
    ]

    canonicalized = TableRowCanonicalizer().canonicalize(rows)

    assert canonicalized[0] == [
        "Maintenance Description",
        "",
        "Frequency",
        "Interval Period",
    ]
    assert canonicalized[1] == [
        "Maintenance",
        "Fire Sliding Door A-60, door type A3000 with drive type E3000mini",
        "",
        "",
    ]


def test_canonicalize_does_not_discard_a_header_row_collapsed_into_one_cell() -> None:
    # Regression guard for a real bug: a header row that collapsed into a
    # single non-empty cell ("TASK INTERVAL DONE COMMENTS", with 2 blank
    # sibling cells -- a real parsing artifact) used to be mistaken for a
    # generic "umbrella" banner row (the existing rule: any lone non-empty
    # cell is automatically an umbrella) and get silently DISCARDED,
    # promoting the first genuine DATA row into its place as if it were the
    # real header -- deleting the table's only interval/frequency
    # information entirely, not just misclassifying it.
    rows = [
        ["", "", "TASK INTERVAL DONE COMMENTS"],
        ["check electrical connections", "annual", ""],
        ["check condition of all electrical wires", "annual", ""],
    ]

    canonicalized = TableRowCanonicalizer().canonicalize(rows)

    assert canonicalized[0] == ["", "", "TASK INTERVAL DONE COMMENTS"]


def test_has_explicit_header_row_recognizes_a_collapsed_multi_word_header_cell() -> None:
    rows = [
        ["", "", "TASK INTERVAL DONE COMMENTS"],
        ["check electrical connections", "annual", ""],
    ]

    assert TableRowCanonicalizer().has_explicit_header_row(rows) is True


def test_has_explicit_header_row_still_rejects_a_lone_ordinary_word_cell() -> None:
    # A single non-empty cell with only 0-1 recognizable header tokens is
    # NOT treated as an explicit header -- this must stay narrow enough to
    # avoid promoting an ordinary short data/title cell.
    rows = [
        ["", "", "Overview"],
        ["some data", "more data", ""],
    ]

    assert TableRowCanonicalizer().has_explicit_header_row(rows) is False


def test_canonicalize_does_not_silently_drop_an_unpairable_row_via_key_value_reshape() -> None:
    # Regression guard for a real bug: when no row qualifies as an
    # explicit header at all, `_canonicalize_key_value_rows` used to
    # silently DROP any row with an odd count of non-empty cells while
    # reshaping the rest into synthetic [Label, Value] pairs -- deleting
    # real content rather than merely failing to parse it.
    rows = [
        ["standalone banner text"],
        ["Model", "XV2000", "Speed", "1450 RPM"],
        ["Weight", "120 kg", "Diameter", "250 mm"],
    ]

    canonicalized = TableRowCanonicalizer().canonicalize(rows)

    assert canonicalized == rows


def test_canonicalize_normalizes_compact_schedule_matrix_rows() -> None:
    rows = [
        ["D", "Q Q", "M S A", "Task Reference"],
        ["General Maintenance Work on the Press"],
        ["X", "General visual inspection daily or after period of particularly high load"],
        ["", "X", "Clean dirt from the housing", "See gearbox Annex"],
    ]

    canonicalized = TableRowCanonicalizer().canonicalize(rows)

    assert canonicalized[0] == [
        "Daily",
        "Quarterly",
        "Monthly",
        "Semi-Annual",
        "Annual",
        "Task",
        "Notes",
    ]
    assert canonicalized[1] == ["", "", "", "", "", "General Maintenance Work on the Press", ""]
    assert canonicalized[2] == [
        "x",
        "",
        "",
        "",
        "",
        "General visual inspection daily or after period of particularly high load",
        "",
    ]
    assert canonicalized[3] == [
        "",
        "x",
        "",
        "",
        "",
        "Clean dirt from the housing",
        "See gearbox Annex",
    ]
