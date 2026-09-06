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
