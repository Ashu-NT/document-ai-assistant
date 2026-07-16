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


def test_reconstruct_returns_original_rows_when_no_toc_pattern_matches() -> None:
    reconstructor = DoclingTocTableRowReconstructor()

    rows = [["Voltage", "400V"], ["Weight", "120 kg"]]

    assert reconstructor.reconstruct(rows) == rows
