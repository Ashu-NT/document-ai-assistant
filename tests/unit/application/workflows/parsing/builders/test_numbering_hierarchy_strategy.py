from src.application.workflows.parsing.builders.section_hierarchy import (
    NumberingHierarchyStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


def make_header(
    element_id: str,
    text: str,
    order_index: int,
    page: int,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.SECTION_HEADER,
        text=text,
        page_start=page,
        page_end=page,
        order_index=order_index,
    )


def test_numbering_strategy_uses_number_depth_for_numbered_headings() -> None:
    headers = [
        make_header("hdr_root", "1 Introduction", 1, 1),
        make_header("hdr_child", "1.2 Lab preparation", 2, 1),
        make_header("hdr_grandchild", "1.2.1 Interrupt handler", 3, 1),
    ]
    strategy = NumberingHierarchyStrategy()

    levels = strategy.assign_levels(headers, headers)

    assert strategy.can_apply(headers, headers) is True
    assert levels["hdr_root"] == 1
    assert levels["hdr_child"] == 2
    assert levels["hdr_grandchild"] == 3


def test_numbering_strategy_uses_contextual_task_number_as_fallback() -> None:
    headers = [
        make_header("hdr_root", "1.3 A first DSP project", 1, 7),
        make_header("hdr_task", "Lab task 1.1: Feeding the ADC input directly to the DAC output", 2, 7),
    ]
    strategy = NumberingHierarchyStrategy()

    levels = strategy.assign_levels(headers, headers, current_levels={"hdr_root": 2})

    assert levels["hdr_task"] == 3
