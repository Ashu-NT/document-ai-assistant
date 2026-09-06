from src.application.workflows.parsing.builders.section_hierarchy.heading_candidates import (
    HeadingCandidateRole,
    HeadingCandidateRoleResolver,
)
from src.application.workflows.parsing.builders.section_hierarchy.section_hierarchy_resolver import (
    SectionHierarchyResolution,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc import (
    TocEntry,
    TocOutline,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import ElementType


def _element(
    element_id: str,
    element_type: ElementType,
    text: str,
    order: int,
    *,
    page: int = 10,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        page_start=page,
        page_end=page,
        order_index=order,
        metadata={"heading_level": 1},
    )


def test_toc_match_does_not_override_stronger_local_table_evidence() -> None:
    headers = [
        _element("h4", ElementType.SECTION_HEADER, "4 Technical Data", 1),
        _element("h42", ElementType.SECTION_HEADER, "4.2 Product Data", 2),
        _element("category", ElementType.SECTION_HEADER, "17 Fluid Data", 3),
        _element("h5", ElementType.SECTION_HEADER, "5 Description", 5),
    ]
    table = _element("table", ElementType.TABLE, "Parameter | Value", 4)
    entry = TocEntry(
        title="Fluid Data",
        normalized_title="fluid data",
        start_page=10,
        level_hint=1,
        numbering="17",
    )
    resolution = SectionHierarchyResolution(
        effective_levels={"h4": 1, "h42": 2, "category": 1, "h5": 1},
        header_numberings={"h4": "4", "h42": "4.2", "category": "17", "h5": "5"},
        toc_outline=TocOutline(
            entries=[entry],
            matched_entries={"category": entry},
        ),
    )

    assessments = HeadingCandidateRoleResolver().resolve(
        headers=headers,
        elements=[headers[0], headers[1], headers[2], table, headers[3]],
        hierarchy_resolution=resolution,
    )

    assert assessments["category"].role == HeadingCandidateRole.TABLE_CATEGORY
    assert assessments["h5"].role == HeadingCandidateRole.OUTLINE_SECTION
    assert "toc_match" in assessments["category"].reasons
    assert "adjacent_table" in assessments["category"].reasons


def test_local_numbered_record_uses_bounded_nearby_table_evidence() -> None:
    headers = [
        _element("h7", ElementType.SECTION_HEADER, "7 Operating Instructions", 1),
        _element("h72", ElementType.SECTION_HEADER, "7.2 Troubleshooting", 2),
        _element("record", ElementType.SECTION_HEADER, "3 - High temperature", 3),
        _element("h73", ElementType.SECTION_HEADER, "7.3 Task Description", 7),
    ]
    elements = [
        headers[0],
        headers[1],
        headers[2],
        _element("code", ElementType.TEXT, "Code: 123", 4),
        _element("description", ElementType.TEXT, "Condition description", 5),
        _element("table", ElementType.TABLE, "Cause | Corrective action", 6),
        headers[3],
    ]
    resolution = SectionHierarchyResolution(
        effective_levels={"h7": 1, "h72": 2, "record": 1, "h73": 2},
        header_numberings={"h7": "7", "h72": "7.2", "record": "3", "h73": "7.3"},
    )

    assessments = HeadingCandidateRoleResolver().resolve(
        headers=headers,
        elements=elements,
        hierarchy_resolution=resolution,
    )

    assert assessments["record"].role == HeadingCandidateRole.TABLE_CATEGORY
    assert assessments["h73"].role == HeadingCandidateRole.OUTLINE_SECTION
    assert "adjacent_table" in assessments["record"].reasons


def test_toc_heading_stays_outline_while_numbered_table_caption_does_not() -> None:
    headers = [
        _element("toc", ElementType.SECTION_HEADER, "Table of Contents", 1, page=2),
        _element("caption", ElementType.SECTION_HEADER, "Table 4-1 Dimensions", 3, page=2),
    ]
    table = _element("table", ElementType.TABLE, "Section | Page", 2, page=2)
    resolution = SectionHierarchyResolution(
        effective_levels={"toc": 1, "caption": 2},
        header_numberings={},
    )

    assessments = HeadingCandidateRoleResolver().resolve(
        headers=headers,
        elements=[headers[0], table, headers[1]],
        hierarchy_resolution=resolution,
    )

    assert assessments["toc"].role == HeadingCandidateRole.OUTLINE_SECTION
    assert assessments["caption"].role == HeadingCandidateRole.CAPTION
