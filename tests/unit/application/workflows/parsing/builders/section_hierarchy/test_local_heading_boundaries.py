from src.application.workflows.parsing.builders import SectionBuilder
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import ElementType
from src.shared.ids import IdGenerator


def _element(
    element_id: str,
    text: str,
    order_index: int,
    *,
    element_type: ElementType = ElementType.SECTION_HEADER,
    level: int = 1,
    page: int = 1,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        order_index=order_index,
        page_start=page,
        page_end=page,
        metadata={"heading_level": level} if element_type == ElementType.SECTION_HEADER else {},
    )


def _text(element_id: str, text: str, order_index: int) -> ParsedCanonicalElement:
    return _element(
        element_id,
        text,
        order_index,
        element_type=ElementType.TEXT,
    )


def test_unique_callout_and_note_reference_remain_local_evidence() -> None:
    elements = [
        _element("h7", "7 Operating Instructions", 1),
        _element("h731", "7.3.1 Oil sampling", 2),
        _element("danger", "Danger of burns and poisoning!", 3),
        _text("danger_body", "Wear protective gloves.", 4),
        _element("note", "Note: 23.", 5),
        _text("note_body", "Reset the service counter.", 6),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert [section.title for section in result.sections] == [
        "7 Operating Instructions",
        "7.3.1 Oil sampling",
    ]
    expected_path = ["7 Operating Instructions", "7.3.1 Oil sampling"]
    assert result.element_section_paths["danger"] == expected_path
    assert result.element_section_paths["note"] == expected_path
    assert elements[2].metadata["heading_candidate_role"] == "local_label"
    assert elements[4].metadata["structural_heading"] is False


def test_colon_ended_labels_remain_local_inside_numbered_scope() -> None:
    elements = [
        _element("h5", "5 Functional Description", 1),
        _element("h52", "5.2 Engine", 2),
        _element("monitoring", "Monitoring:", 3),
        _text("monitoring_body", "The controller monitors oil pressure.", 4),
        _element("control", "Control mode:", 5),
        _text("control_body", "Speed control is enabled.", 6),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert [section.title for section in result.sections] == [
        "5 Functional Description",
        "5.2 Engine",
    ]
    expected_path = ["5 Functional Description", "5.2 Engine"]
    assert result.element_section_paths["monitoring_body"] == expected_path
    assert result.element_section_paths["control_body"] == expected_path


def test_repeated_page_continuation_heading_keeps_first_structural_heading() -> None:
    elements = [
        _element("h7", "7 Operating Instructions", 1),
        _element("h738", "7.3.8 Fuel filter", 2),
        _element(
            "first",
            "Replacing filter element with the engine running",
            3,
            level=3,
            page=10,
        ),
        _text("first_body", "Switch to the other filter.", 4),
        _element(
            "continued",
            "Replacing filter element with the engine running",
            5,
            level=3,
            page=11,
        ),
        _text("continued_body", "Drain the isolated filter.", 6),
    ]

    result = SectionBuilder(IdGenerator()).build("doc_001", elements)

    assert [section.title for section in result.sections] == [
        "7 Operating Instructions",
        "7.3.8 Fuel filter",
        "Replacing filter element with the engine running",
    ]
    section_path = [
        "7 Operating Instructions",
        "7.3.8 Fuel filter",
        "Replacing filter element with the engine running",
    ]
    assert result.element_section_paths["first_body"] == section_path
    assert result.element_section_paths["continued"] == section_path
    assert result.element_section_paths["continued_body"] == section_path
    assert elements[4].metadata["heading_candidate_role"] == "local_label"
