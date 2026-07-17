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


def test_reconstruct_keeps_rows_where_a_multi_segment_dot_leader_has_a_stray_space() -> (
    None
):
    # Regression guard for a real bug: a dotted leader can get broken into
    # more than one dot-run with a stray space in between (e.g.
    # "..... ..... 30" instead of a single clean run of dots), which the
    # single-segment dot-tolerant pattern still failed to recognize as a
    # page-number cell, silently dropping the row.
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "11"],
            ["", "1.1 Introduction ................................", "................................ ......... 12"],
            ["2 Safety", "15"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["1.1", "Introduction", "12"],
        ["2", "Safety", "15"],
    ]


def test_reconstruct_handles_numbering_with_stray_spaces_around_the_decimal_point() -> (
    None
):
    # Regression guard for a real bug: numbering like "7.3" can come back
    # from extraction as "7 . 3" (a font-kerning/glyph-spacing artifact).
    # This used to break the number/title split entirely, misreading "3" as
    # the start of the title and corrupting the numbering to just "7" --
    # which then made two genuinely distinct entries look identical and
    # get merged together by a later repair pass.
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "11"],
            ["7 . 3", "Door type A3000 Module B - Double door", "43"],
            ["7 . 4", "Drive type E3000mini Module B", "45"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["7.3", "Door type A3000 Module B - Double door", "43"],
        ["7.4", "Drive type E3000mini Module B", "45"],
    ]


def test_reconstruct_handles_lettered_appendix_and_annex_numbering() -> None:
    # TOC numbering isn't always purely numeric -- lettered appendices/annexes
    # ("A", "A.1", "B") are a common, generic convention, not a one-off.
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "11"],
            ["A Appendix Overview", "40"],
            ["A.1 Wiring diagrams", "41"],
            ["B Annex Certificates", "45"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["A", "Appendix Overview", "40"],
        ["A.1", "Wiring diagrams", "41"],
        ["B", "Annex Certificates", "45"],
    ]


def test_reconstruct_does_not_treat_an_ordinary_title_word_as_numbering() -> None:
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "11"],
            ["Overview", "12"],
            ["2 Safety", "15"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["", "Overview", "12"],
        ["2", "Safety", "15"],
    ]


def test_reconstruct_returns_original_rows_when_no_toc_pattern_matches() -> None:
    reconstructor = DoclingTocTableRowReconstructor()

    rows = [["Voltage", "400V"], ["Weight", "120 kg"]]

    assert reconstructor.reconstruct(rows) == rows


def test_reconstruct_handles_roman_numeral_front_matter_pages() -> None:
    # A book's front matter commonly uses roman-numeral pages ("i, ii,
    # iii...") while the main body switches to Arabic digits -- these rows
    # have no numbering column at all (a common front-matter TOC shape), so
    # this also exercises the root-TOC-title fallback gate.
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["Foreword", "iii"],
            ["Contents", "iv"],
            ["Figures", "vi"],
            ["Abbreviations", "vii"],
        ]
    )

    assert rows == [
        ["Title", "Page"],
        ["Foreword", "iii"],
        ["Contents", "iv"],
        ["Figures", "vi"],
        ["Abbreviations", "vii"],
    ]


def test_reconstruct_preserves_roman_and_arabic_pages_in_the_same_table_without_conflating_them() -> (
    None
):
    # A single TOC can mix a roman-numeral front matter section with an
    # Arabic-numbered main body -- these must never collapse to the same
    # value (e.g. roman "III" and Arabic "3" are visually similar but are
    # NOT the same page), so the original page text must survive verbatim.
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "III"],
            ["1.1 Introduction", "IV"],
            ["2 Safety", "3"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "III"],
        ["1.1", "Introduction", "IV"],
        ["2", "Safety", "3"],
    ]


def test_reconstruct_handles_lowercase_bare_cell_numbering() -> None:
    # An isolated cell containing ONLY a lowercase letter (e.g. "a", with no
    # other text in that cell) is overwhelmingly likely to be genuine
    # lettered numbering, not a coincidental lone word -- unlike a
    # lowercase-led combined cell, which stays excluded (see the negative
    # test below).
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "11"],
            ["a", "First appendix topic", "12"],
            ["b", "Second appendix topic", "13"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["a", "First appendix topic", "12"],
        ["b", "Second appendix topic", "13"],
    ]


def test_reconstruct_does_not_split_a_lowercase_led_combined_cell_as_numbering() -> (
    None
):
    # Unlike the isolated-cell case above, a combined "numbering + title" cell
    # must stay upper-case/digit-only -- otherwise ordinary two-word phrases
    # led by a short lowercase word ("of course", "to install") would be
    # misread as "numbering + title" and incorrectly split.
    reconstructor = DoclingTocTableRowReconstructor()

    rows = reconstructor.reconstruct(
        [
            ["1 Preface", "11"],
            ["of course this works", "12"],
            ["2 Safety", "15"],
        ]
    )

    assert rows == [
        ["Number", "Title", "Page"],
        ["1", "Preface", "11"],
        ["", "of course this works", "12"],
        ["2", "Safety", "15"],
    ]
