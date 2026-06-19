from src.application.workflows.parsing.builders import SectionBuilder
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType
from src.shared.ids import IdGenerator


def make_element(
    element_id: str,
    element_type: ElementType,
    text: str,
    order_index: int,
    metadata: dict | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        order_index=order_index,
        metadata=metadata or {},
    )


def test_section_builder_assigns_non_header_elements_to_active_section() -> None:
    elements = [
        make_element("hdr_1", ElementType.SECTION_HEADER, "Introduction", 1, {"heading_level": 1}),
        make_element("txt_1", ElementType.TEXT, "Intro body", 2),
        make_element("hdr_2", ElementType.SECTION_HEADER, "Overview", 3, {"heading_level": 2}),
        make_element("txt_2", ElementType.TEXT, "Overview body", 4),
    ]
    builder = SectionBuilder(IdGenerator())

    result = builder.build("doc_001", elements)

    intro_section_id = result.header_section_ids["hdr_1"]
    overview_section_id = result.header_section_ids["hdr_2"]
    assert result.element_section_ids["txt_1"] == intro_section_id
    assert result.element_section_ids["txt_2"] == overview_section_id
    assert result.element_section_paths["txt_2"] == ["Introduction", "Overview"]


def test_section_builder_creates_default_root_when_no_headers_exist() -> None:
    elements = [
        make_element("txt_1", ElementType.TEXT, "Overview body", 1),
    ]
    builder = SectionBuilder(IdGenerator())

    result = builder.build("doc_001", elements)

    assert len(result.sections) == 1
    assert result.sections[0].title == "Document"
    assert result.element_section_paths["txt_1"] == ["Document"]


def test_section_builder_populates_parent_ids_and_paths_for_nested_sections() -> None:
    elements = [
        make_element("hdr_1", ElementType.SECTION_HEADER, "Introduction", 1, {"heading_level": 1}),
        make_element("hdr_2", ElementType.SECTION_HEADER, "Overview", 2, {"heading_level": 2}),
    ]
    builder = SectionBuilder(IdGenerator())

    result = builder.build("doc_001", elements)
    sections_by_title = {section.title: section for section in result.sections}

    assert sections_by_title["Overview"].parent_section_id == sections_by_title["Introduction"].section_id
    assert sections_by_title["Overview"].section_path == ["Introduction", "Overview"]
