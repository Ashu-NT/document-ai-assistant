from src.application.workflows.parsing.builders.section_hierarchy import (
    HeadingLevelStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


def make_header(element_id: str, text: str, level: int | None) -> CanonicalElement:
    metadata = {}
    if level is not None:
        metadata["heading_level"] = level

    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.SECTION_HEADER,
        text=text,
        order_index=int(element_id.split("_")[-1]),
        metadata=metadata,
    )


def test_heading_level_strategy_preserves_mixed_levels() -> None:
    headers = [
        make_header("hdr_1", "Introduction", 1),
        make_header("hdr_2", "Overview", 2),
        make_header("hdr_3", "Details", 3),
    ]
    strategy = HeadingLevelStrategy()

    levels = strategy.assign_levels(headers, headers)

    assert strategy.can_apply(headers, headers) is True
    assert levels == {
        "hdr_1": 1,
        "hdr_2": 2,
        "hdr_3": 3,
    }


def test_heading_level_strategy_treats_all_level_one_as_weak() -> None:
    headers = [
        make_header("hdr_1", "Introduction", 1),
        make_header("hdr_2", "Overview", 1),
        make_header("hdr_3", "Details", 1),
    ]
    strategy = HeadingLevelStrategy()

    assert strategy.assign_levels(headers, headers) == {
        "hdr_1": 1,
        "hdr_2": 1,
        "hdr_3": 1,
    }
    assert strategy.can_apply(headers, headers) is False
