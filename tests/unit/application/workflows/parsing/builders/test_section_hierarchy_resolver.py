from src.application.workflows.parsing.builders.section_hierarchy import (
    SectionHierarchyResolver,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


def make_element(
    element_id: str,
    element_type: ElementType,
    text: str,
    order_index: int,
    page: int,
    metadata: dict | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        order_index=order_index,
        page_start=page,
        page_end=page,
        metadata=metadata or {},
    )


def test_resolver_uses_docling_levels_when_they_are_useful() -> None:
    elements = [
        make_element("hdr_1", ElementType.SECTION_HEADER, "Introduction", 1, 1, {"heading_level": 1}),
        make_element("hdr_2", ElementType.SECTION_HEADER, "Overview", 2, 1, {"heading_level": 2}),
        make_element("hdr_3", ElementType.SECTION_HEADER, "Details", 3, 1, {"heading_level": 3}),
    ]

    resolution = SectionHierarchyResolver().resolve(elements)

    assert resolution.effective_levels == {
        "hdr_1": 1,
        "hdr_2": 2,
        "hdr_3": 3,
    }
    assert resolution.sources["hdr_2"] == "docling_level"


def test_resolver_falls_back_to_toc_when_all_docling_levels_are_one() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Table of Contents", 1, 2, {"heading_level": 1}),
        make_element("tbl_toc", ElementType.TABLE, "| Introduction .... 3 |\n| Chapter Two .... 5 |", 2, 2),
        make_element("hdr_intro", ElementType.SECTION_HEADER, "Introduction", 3, 3, {"heading_level": 1}),
        make_element("hdr_child", ElementType.SECTION_HEADER, "Overview", 4, 4, {"heading_level": 1}),
        make_element("hdr_root_2", ElementType.SECTION_HEADER, "Chapter Two", 5, 5, {"heading_level": 1}),
    ]

    resolution = SectionHierarchyResolver().resolve(elements)

    assert resolution.effective_levels["hdr_intro"] == 1
    assert resolution.effective_levels["hdr_child"] == 2
    assert resolution.sources["hdr_child"] == "toc_page_range"


def test_resolver_applies_layout_refinement_inside_toc_ranges() -> None:
    elements = [
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Table of Contents", 1, 2, {"heading_level": 1}),
        make_element("tbl_toc", ElementType.TABLE, "| Oscilloscope Probes .... 26 |", 2, 2),
        make_element("hdr_root", ElementType.SECTION_HEADER, "Oscilloscope Probes", 3, 26, {"heading_level": 1}),
        make_element("hdr_child", ElementType.SECTION_HEADER, "Loading", 4, 26, {"heading_level": 1}),
        make_element("hdr_grandchild", ElementType.SECTION_HEADER, "Resistive loading", 5, 26, {"heading_level": 1}),
    ]

    resolution = SectionHierarchyResolver().resolve(elements)

    assert resolution.effective_levels["hdr_root"] == 1
    assert resolution.effective_levels["hdr_child"] == 2
    assert resolution.effective_levels["hdr_grandchild"] == 3
    assert resolution.sources["hdr_grandchild"] == "layout_heuristic"


def test_resolver_uses_structured_contents_and_explicit_parent_hints() -> None:
    elements = [
        make_element("hdr_cover", ElementType.SECTION_HEADER, "DP Lab", 1, 1, {"heading_level": 1}),
        make_element("hdr_toc", ElementType.SECTION_HEADER, "Contents", 2, 3, {"heading_level": 1}),
        make_element(
            "tbl_toc",
            ElementType.TABLE,
            "",
            3,
            3,
            metadata={
                "item_label": "document_index",
                "table_rows": [
                    ["1 Sampling and quantization", "", "", "5"],
                    ["", "1.2", "Lab preparation", "5"],
                    ["", "", "1.2.1 Interrupt handler and bit manipulation", "6"],
                    ["", "1.3", "A first DSP project with Code Composer Studio", "7"],
                    ["", "", "1.3.3 Overflows", "8"],
                ],
            },
        ),
        make_element("hdr_root", ElementType.SECTION_HEADER, "Sampling and quantization", 4, 5, {"heading_level": 1}),
        make_element("hdr_1_2", ElementType.SECTION_HEADER, "1.2 Lab preparation", 5, 5, {"heading_level": 1}),
        make_element("hdr_prep", ElementType.SECTION_HEADER, "Prep task (for lab entry test)", 6, 6, {"heading_level": 1}),
        make_element(
            "hdr_1_2_1",
            ElementType.SECTION_HEADER,
            "1.2.1 Interrupt handler and bit manipulation",
            7,
            6,
            {"heading_level": 1},
        ),
        make_element(
            "hdr_1_3",
            ElementType.SECTION_HEADER,
            "1.3 A first DSP project with Code Composer Studio",
            8,
            7,
            {"heading_level": 1},
        ),
        make_element(
            "hdr_lab_task",
            ElementType.SECTION_HEADER,
            "Lab task 1.1: Feeding the ADC input directly to the DAC output",
            9,
            7,
            {"heading_level": 1},
        ),
        make_element(
            "hdr_local_step",
            ElementType.SECTION_HEADER,
            "1. Function test of the program",
            10,
            7,
            {"heading_level": 1},
        ),
        make_element("hdr_1_3_3", ElementType.SECTION_HEADER, "1.3.3 Overflows", 11, 8, {"heading_level": 1}),
    ]

    resolution = SectionHierarchyResolver().resolve(elements)

    assert resolution.effective_levels["hdr_root"] == 1
    assert resolution.effective_levels["hdr_1_2"] == 2
    assert resolution.effective_levels["hdr_1_2_1"] == 3
    assert resolution.effective_levels["hdr_1_3"] == 2
    assert resolution.effective_levels["hdr_1_3_3"] == 3
    assert resolution.explicit_parent_headers["hdr_1_3_3"] == "hdr_1_3"
    assert resolution.explicit_parent_headers["hdr_prep"] == "hdr_1_2"
    assert resolution.explicit_parent_headers["hdr_lab_task"] == "hdr_1_3"
