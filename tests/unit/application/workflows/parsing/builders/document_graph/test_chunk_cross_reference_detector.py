from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_cross_reference_detector import (
    ChunkCrossReferenceDetector,
)


def _detector() -> ChunkCrossReferenceDetector:
    return ChunkCrossReferenceDetector()


def test_detects_arrow_page_reference() -> None:
    # Real document: this exact pattern occurs 592 times in one document
    # alone (SA18000434_00E.pdf).
    result = _detector().detect("3. Contact Service. (→ Page 1062)")

    assert len(result.page_references) == 1
    assert result.page_references[0].target_page == 1062
    assert result.page_references[0].matched_text == "(→ Page 1062)"


def test_detects_see_page_reference() -> None:
    result = _detector().detect("For details, see page 78 of this manual.")

    assert len(result.page_references) == 1
    assert result.page_references[0].target_page == 78


def test_detects_parenthesized_see_page_reference() -> None:
    result = _detector().detect("Refer to the wiring diagram (see page 45).")

    assert len(result.page_references) == 1
    assert result.page_references[0].target_page == 45


def test_detects_multiple_distinct_page_references_in_one_chunk() -> None:
    # Real document shape: a troubleshooting table with one action row per
    # line, each ending in its own distinct page reference.
    content = (
        "1. Check state of charge of the batteries. (→ Page 242) "
        "2. Check battery-charging generator. (→ Page 223) "
        "3. Contact Service. (→ Page 1062)"
    )
    result = _detector().detect(content)

    assert sorted(ref.target_page for ref in result.page_references) == [
        223,
        242,
        1062,
    ]


def test_does_not_double_count_overlapping_pattern_matches() -> None:
    # "(-> Page N)" and "see page N" could both match the same span if not
    # tracked carefully; real corpus content never actually nests them, but
    # the detector must not double-count a single arrow-page reference just
    # because it's re-scanned by a later, looser pattern.
    result = _detector().detect("(→ Page 100)")

    assert len(result.page_references) == 1


def test_combined_see_chapter_and_page_reference_is_recorded_as_a_page_reference() -> (
    None
):
    # Real document: "see Chapter 9.3.5 Lubrication oil, Page 143" -- a
    # hybrid form that includes both a section number AND a page number.
    # Must be captured whole as a resolvable PAGE reference, not just as a
    # bare "see chapter 9.3.5" section-only reference.
    result = _detector().detect(
        "see Chapter 9.3.5 Lubrication oil, Page 143 for more information."
    )

    assert len(result.page_references) == 1
    assert result.page_references[0].target_page == 143
    assert result.section_references == []


def test_ignores_bare_page_number_pagination_footers() -> None:
    # Corpus-verified: bare "Page N"/"p. N" (no "see"/arrow prefix) are
    # ~85%+ PDF pagination footer noise ("Page 1 of 2", "p. 1/10"), not
    # same-document navigation -- deliberately not detected.
    result = _detector().detect("Certificate no: Page 1 of 1\np. 2/10")

    assert result.page_references == []


def test_detects_section_reference_with_no_page_number() -> None:
    # Real document: "Refer to chap. 8.9 to access the valve." -- genuine
    # same-document navigation, corpus-verified, but detected-only in v1
    # (see ChunkCrossReferenceType.SECTION_REFERENCE).
    result = _detector().detect("Refer to chap. 8.9 to access the valve.")

    assert len(result.section_references) == 1
    assert result.section_references[0].target_section_label == "8.9"


def test_detects_see_section_reference() -> None:
    result = _detector().detect("See section 6 for wiring details.")

    assert len(result.section_references) == 1
    assert result.section_references[0].target_section_label == "6"


def test_does_not_record_a_redundant_section_reference_for_an_already_captured_page_reference() -> (
    None
):
    # The combined "see chapter X.X ..., Page N" pattern already consumes
    # this text as a page reference -- the bare "see chapter" section
    # pattern must not also fire on the same span.
    result = _detector().detect("see Chapter 2.3 Display and meaning, Page 16.")

    assert len(result.page_references) == 1
    assert result.section_references == []


def test_returns_empty_result_for_plain_text() -> None:
    result = _detector().detect("Tighten the bolts to the specified torque.")

    assert result.page_references == []
    assert result.section_references == []


def test_returns_empty_result_for_empty_content() -> None:
    result = _detector().detect("")

    assert result.page_references == []
    assert result.section_references == []


def test_rejects_implausible_page_numbers() -> None:
    result = _detector().detect("(→ Page 0)")

    assert result.page_references == []


def test_detects_see_table_reference() -> None:
    # Generic English idiom, not corpus-verified against a specific
    # shipyard document (unlike the page-reference patterns above) -- see
    # the caveat comment on _TABLE_REFERENCE_PATTERNS.
    result = _detector().detect("Spare parts are listed in see Table 3 below.")

    assert len(result.table_references) == 1
    assert result.table_references[0].target_asset_label == "3"


def test_detects_table_above_below_reference() -> None:
    result = _detector().detect("Table 3.2 above lists the recommended torque values.")

    assert len(result.table_references) == 1
    assert result.table_references[0].target_asset_label == "3.2"


def test_detects_see_figure_reference() -> None:
    result = _detector().detect("The assembly is shown in see Figure 2.")

    assert len(result.figure_references) == 1
    assert result.figure_references[0].target_asset_label == "2"


def test_detects_abbreviated_fig_reference() -> None:
    result = _detector().detect("Refer to fig. 5 for the wiring diagram.")

    assert len(result.figure_references) == 1
    assert result.figure_references[0].target_asset_label == "5"


def test_does_not_detect_drawing_id_references() -> None:
    # Deliberately out of scope -- see the caveat comment on
    # _TABLE_REFERENCE_PATTERNS/_FIGURE_REFERENCE_PATTERNS.
    result = _detector().detect("See Drawing SK-1044 for dimensions.")

    assert result.table_references == []
    assert result.figure_references == []
