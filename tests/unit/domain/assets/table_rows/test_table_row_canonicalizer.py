from src.domain.assets.table_rows.table_row_canonicalizer import (
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
