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
