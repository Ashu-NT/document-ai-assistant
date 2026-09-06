from dataclasses import dataclass

from src.domain.common import ElementType


@dataclass(slots=True, frozen=True)
class HeadingCandidateSignals:
    numbering: str | None
    numbering_depth: int | None
    active_scope_depth: int | None
    numbering_compatible: bool | None
    implausible_hierarchy_jump: bool
    toc_matched: bool
    toc_title_exact: bool
    toc_number_exact: bool
    toc_page_close: bool
    native_heading_level: int | None
    has_descendant_pattern: bool
    has_sibling_pattern: bool
    next_element_type: ElementType | None
    next_element_same_page: bool
    next_element_order_gap: int | None
    repeated_title_count: int
    embedded_item_numbering: bool
    layout_prominent: bool
    indented_from_active: bool
    page_continuous: bool
    caption_like: bool
    noise_like: bool
    title_word_count: int
    ends_with_colon: bool

    @property
    def adjacent_table(self) -> bool:
        return (
            self.next_element_type == ElementType.TABLE
            and self.next_element_same_page
            and (self.next_element_order_gap or 10_000) <= 3
        )

    @property
    def adjacent_picture(self) -> bool:
        return (
            self.next_element_type == ElementType.PICTURE
            and self.next_element_same_page
            and (self.next_element_order_gap or 10_000) <= 3
        )
