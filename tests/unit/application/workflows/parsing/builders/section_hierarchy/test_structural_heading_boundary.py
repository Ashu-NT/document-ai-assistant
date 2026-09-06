from src.application.workflows.parsing.builders import SectionBuilder
from src.application.workflows.parsing.builders.section_hierarchy.numbering.section_parent_link_validator import (
    SectionParentLinkValidator,
)
from src.application.workflows.parsing.builders.section_hierarchy.section_hierarchy_resolver import (
    SectionHierarchyResolver,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import ElementType
from src.shared.ids import IdGenerator


def _header(
    element_id: str,
    text: str,
    order_index: int,
    *,
    level: int = 1,
    page: int = 1,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.SECTION_HEADER,
        text=text,
        order_index=order_index,
        page_start=page,
        page_end=page,
        metadata={"heading_level": level},
    )


def _text(element_id: str, text: str, order_index: int) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TEXT,
        text=text,
        order_index=order_index,
        page_start=1,
        page_end=1,
    )


def _table(element_id: str, text: str, order_index: int) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text=text,
        order_index=order_index,
        page_start=1,
        page_end=1,
    )


def test_active_numbered_scope_owns_local_subheads_until_next_peer() -> None:
    headers = [
        _header("h2", "2 Safety", 1),
        _header("h22", "2.2 Intended applications", 2),
        _header("h_local_1", "Permitted operation", 3),
        _header("h_local_2", "Modifications or conversions", 4),
        _header("h23", "2.3 Personnel requirements", 5),
    ]

    resolution = SectionHierarchyResolver().resolve(headers)

    assert resolution.explicit_parent_headers["h22"] == "h2"
    assert resolution.explicit_parent_headers["h_local_1"] == "h22"
    assert resolution.explicit_parent_headers["h_local_2"] == "h22"
    assert resolution.explicit_parent_headers["h23"] == "h2"


def test_consecutive_local_subheads_remain_peers() -> None:
    headers = [
        _header("h2", "2 Safety", 1),
        _header("h25", "2.5 Service safety", 2),
        _header("h_a", "Tools and lifting", 3),
        _header("h_b", "Installation and cleanliness", 4),
        _header("h_c", "Lines and connections", 5),
    ]

    resolution = SectionHierarchyResolver().resolve(headers)

    assert resolution.explicit_parent_headers["h_a"] == "h25"
    assert resolution.explicit_parent_headers["h_b"] == "h25"
    assert resolution.explicit_parent_headers["h_c"] == "h25"
    assert resolution.effective_levels["h_a"] == 3
    assert resolution.effective_levels["h_b"] == 3
    assert resolution.effective_levels["h_c"] == 3


def test_local_callouts_remain_evidence_without_becoming_sections() -> None:
    elements = [
        _header("root", "3 Maintenance", 1),
        _header("warning", "WARNING", 2, level=2),
        _text("warning_text", "Disconnect power before service.", 3),
        _header("cause_1", "Cause", 4, level=2),
        _text("cause_text_1", "A filter is blocked.", 5),
        _header("cause_2", "Cause", 6, level=2),
        _text("cause_text_2", "A valve is closed.", 7),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert [section.title for section in result.sections] == ["3 Maintenance"]
    assert elements[1].metadata["structural_heading"] is False
    assert elements[3].metadata["structural_heading"] is False
    assert result.element_section_paths["warning"] == ["3 Maintenance"]
    assert result.element_section_paths["cause_text_2"] == ["3 Maintenance"]


def test_parent_link_validator_rejects_links_beyond_maximum_depth() -> None:
    headers = [_header(f"h{i}", f"Heading {i}", i) for i in range(1, 8)]
    links = {f"h{i}": f"h{i - 1}" for i in range(2, 8)}

    SectionParentLinkValidator(max_depth=6).validate(headers, links)

    assert "h7" not in links


def test_repeated_procedure_role_headers_remain_local_evidence() -> None:
    elements = [
        _header("task_1", "8.1 Checking filter", 1),
        _header("pre_1", "Preconditions", 2, level=2),
        _text("body_1", "Shut down the engine.", 3),
        _header("task_2", "8.2 Checking pump", 4),
        _header("pre_2", "Preconditions", 5, level=2),
        _text("body_2", "Close the isolation valve.", 6),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert [section.title for section in result.sections] == [
        "8.1 Checking filter",
        "8.2 Checking pump",
    ]
    assert elements[1].metadata["structural_heading"] is False
    assert elements[4].metadata["structural_heading"] is False
    assert result.element_section_paths["pre_2"] == ["8.2 Checking pump"]


def test_embedded_numbered_headings_do_not_reset_active_document_scope() -> None:
    elements = [
        _header("h4", "4 Technical Data", 1),
        _header("h42", "4.2 Product data", 2),
        _header("record_1", "1. Power-related data", 3),
        _table("table_1", "Parameter | Value", 4),
        _header("record_11", "11. Fuel system", 5),
        _table("table_11", "Parameter | Value", 6),
        _header("h5", "5 Functional Description", 7),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert [section.title for section in result.sections] == [
        "4 Technical Data",
        "4.2 Product data",
        "5 Functional Description",
    ]
    expected_path = ["4 Technical Data", "4.2 Product data"]
    assert result.element_section_paths["record_1"] == expected_path
    assert result.element_section_paths["table_11"] == expected_path
    assert elements[2].metadata["heading_candidate_role"] == "table_category"
    assert elements[4].metadata["heading_candidate_role"] == "table_category"


def test_same_page_child_before_parent_is_recovered_without_reordering_content() -> None:
    headers = [
        _header("h41", "4.1 Main dimensions", 1, page=35),
        _header("h4", "4 Technical Data", 2, page=35),
        _header("h42", "4.2 Product data", 3, page=36),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", headers)

    by_title = {section.title: section for section in result.sections}
    assert (
        by_title["4.1 Main dimensions"].parent_section_id == by_title["4 Technical Data"].section_id
    )
    assert by_title["4.1 Main dimensions"].section_path == [
        "4 Technical Data",
        "4.1 Main dimensions",
    ]
    assert by_title["4.2 Product data"].section_path == [
        "4 Technical Data",
        "4.2 Product data",
    ]


def test_forward_parent_on_another_page_is_not_accepted() -> None:
    headers = [
        _header("h41", "4.1 Main dimensions", 1, page=34),
        _header("h4", "4 Technical Data", 2, page=35),
    ]

    resolution = SectionHierarchyResolver().resolve(headers)

    assert "h41" not in resolution.explicit_parent_headers


def test_numbered_alarm_records_remain_inside_active_catalog_scope() -> None:
    elements = [
        _header("h7", "7 Operating Instructions", 1),
        _header("h72", "7.2 Troubleshooting", 2),
        _header("alarm_641", "641 - System reset by watchdog", 3),
        _text("alarm_641_body", "Check the event log.", 4),
        _header("alarm_625", "625 - Fuel pressure alarm", 5),
        _text("alarm_625_body", "Inspect the pressure sensor.", 6),
        _header("h8", "8 Component Exchange", 7),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert [section.title for section in result.sections] == [
        "7 Operating Instructions",
        "7.2 Troubleshooting",
        "8 Component Exchange",
    ]
    expected_path = ["7 Operating Instructions", "7.2 Troubleshooting"]
    assert result.element_section_paths["alarm_641"] == expected_path
    assert result.element_section_paths["alarm_625_body"] == expected_path
    assert elements[2].metadata["heading_candidate_role"] == "local_label"


def test_short_numbered_record_with_nearby_table_does_not_reset_outline() -> None:
    elements = [
        _header("h7", "7 Operating Instructions", 1),
        _header("h72", "7.2 Troubleshooting", 2),
        _header("record_3", "3 - High temperature", 3),
        _text("record_code", "Code: 123", 4),
        _text("record_description", "The measured value exceeded its limit.", 5),
        _table("record_actions", "Cause | Corrective action", 6),
        _header("h73", "7.3 Task Description", 7),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert [section.title for section in result.sections] == [
        "7 Operating Instructions",
        "7.2 Troubleshooting",
        "7.3 Task Description",
    ]
    troubleshooting_path = ["7 Operating Instructions", "7.2 Troubleshooting"]
    assert result.element_section_paths["record_3"] == troubleshooting_path
    assert result.element_section_paths["record_actions"] == troubleshooting_path
    assert elements[2].metadata["heading_candidate_role"] == "table_category"
