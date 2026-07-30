from src.application.workflows.parsing.builders.section_hierarchy import (
    LayoutHeuristicStrategy,
)
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.domain.common import ElementType


def make_header(
    element_id: str,
    text: str,
    order_index: int,
    page: int,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.SECTION_HEADER,
        text=text,
        page_start=page,
        page_end=page,
        order_index=order_index,
    )


def test_layout_strategy_infers_numbered_heading_levels() -> None:
    headers = [
        make_header("hdr_1", "1 Introduction", 1, 1),
        make_header("hdr_2", "1.1 Overview", 2, 1),
        make_header("hdr_3", "1.1.1 Details", 3, 1),
    ]
    strategy = LayoutHeuristicStrategy()

    levels = strategy.assign_levels(headers, headers)

    assert levels["hdr_1"] == 1
    assert levels["hdr_2"] == 2
    assert levels["hdr_3"] == 3


def test_layout_strategy_can_refine_short_child_headings() -> None:
    headers = [
        make_header("root", "Oscilloscope Probes", 1, 26),
        make_header("loading", "Loading", 2, 26),
        make_header("resistive", "Resistive loading", 3, 26),
        make_header("capacitive", "Capacitive loading", 4, 26),
    ]
    strategy = LayoutHeuristicStrategy()

    levels = strategy.assign_levels(
        headers,
        headers,
        current_levels={
            "root": 1,
            "loading": 2,
            "resistive": 2,
            "capacitive": 2,
        },
    )

    assert levels["loading"] == 2
    assert levels["resistive"] == 3
    assert levels["capacitive"] == 3


def make_text(element_id: str, text: str, order_index: int, page: int) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=text,
        page_start=page,
        page_end=page,
        order_index=order_index,
    )


def test_layout_strategy_nests_umbrella_child_within_text_length_threshold() -> None:
    """Exercises the on-demand text-between computation (prefix-sum lookup)
    directly, with real TEXT elements interspersed between headers, rather
    than the zero-text-between case the other umbrella test covers."""
    headers = [
        make_header("root", "Controls", 1, 1),
        make_header("child", "Brightness", 3, 1),
    ]
    elements = [
        headers[0],
        make_text("txt_1", "x" * 100, 2, 1),
        headers[1],
    ]
    strategy = LayoutHeuristicStrategy()

    levels = strategy.assign_levels(
        headers,
        elements,
        current_levels={"root": 1, "child": 3},
    )

    # Nesting succeeds (100 chars &lt;= 220-char threshold), so "child" is
    # renested one level below "root" (level 2), overriding its given
    # level 3 -- proving the on-demand text-between computation matched
    # the expected byte count rather than defaulting to 0/unmatched.
    assert levels["child"] == 2


def test_layout_strategy_does_not_nest_umbrella_child_beyond_text_length_threshold() -> None:
    headers = [
        make_header("root", "Controls", 1, 1),
        make_header("child", "Brightness", 3, 1),
    ]
    elements = [
        headers[0],
        make_text("txt_1", "x" * 300, 2, 1),
        headers[1],
    ]
    strategy = LayoutHeuristicStrategy()

    levels = strategy.assign_levels(
        headers,
        elements,
        current_levels={"root": 1, "child": 3},
    )

    # 300 characters of text between root and child exceeds the 220-char
    # umbrella-nesting threshold, so "child" should stay at its given level
    # rather than being renested under "root".
    assert levels["child"] == 3


def test_layout_strategy_does_not_overnest_unrelated_roots() -> None:
    headers = [
        make_header("intro", "Introduction", 1, 3),
        make_header("overview", "Overview", 2, 3),
        make_header("conclusion", "Conclusion", 3, 28),
    ]
    strategy = LayoutHeuristicStrategy()

    levels = strategy.assign_levels(
        headers,
        headers,
        current_levels={
            "intro": 1,
            "overview": 2,
            "conclusion": 1,
        },
    )

    assert levels["conclusion"] == 1
