from src.application.workflows.parsing.normalizers.docling_toc_table_row_reconstructor import (
    DoclingTocTableRowReconstructor,
)


def test_reconstruct_parses_english_toc_rows_with_numbering() -> None:
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "11"],
            ["1.1 Introduction", "12"],
            ["2 Safety", "15"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["1.1", "Introduction", "12"],
        ["2", "Safety", "15"],
    ]


def test_reconstruct_handles_non_english_titles_using_only_digit_patterns() -> None:
    """The reconstructor must never depend on English header/title words --
    only on digit-based numbering/page patterns -- so it works identically
    for a non-English manual's table of contents."""
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Consignes de sécurité", "12"],
            ["1.1 Étalonnage et réglage", "27"],
            ["2 Dépannage", "41"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Consignes de sécurité", "12"],
        ["1.1", "Étalonnage et réglage", "27"],
        ["2", "Dépannage", "41"],
    ]


def test_reconstruct_keeps_rows_where_a_dot_leader_remnant_sticks_to_the_page_cell() -> (
    None
):
    # Regression guard for a real, high-impact bug: a table's dotted leader
    # ("......") between title and page number commonly gets split across
    # two adjacent cells at an arbitrary point, leaving a few residual
    # leader dots stuck to the page-number cell (e.g. "..18" instead of a
    # clean "18"). The row-level page-cell check used to require the cell
    # to be composed of ONLY digits, so every row shaped like this was
    # silently dropped from the reconstructed table entirely -- on a real
    # document this discarded roughly half of a multi-page TOC's entries.
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "11"],
            ["1.1 Introduction", "..12"],
            ["1.2 Scope", "...13"],
            ["2 Safety", "15"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["1.1", "Introduction", "12"],
        ["1.2", "Scope", "13"],
        ["2", "Safety", "15"],
    ]


def test_reconstruct_returns_original_rows_when_no_toc_pattern_matches() -> None:
    reconstructor = DoclingTocTableRowReconstructor()

    rows = [["Voltage", "400V"], ["Weight", "120 kg"]]

    assert reconstructor.reconstruct(rows) == rows
