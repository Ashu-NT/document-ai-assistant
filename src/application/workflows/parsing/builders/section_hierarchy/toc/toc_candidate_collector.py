from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry_parser import (
    TocEntryParser,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


class TocCandidateCollector:
    _TOC_ELEMENT_TYPES = {
        ElementType.TABLE,
        ElementType.TEXT,
        ElementType.LIST_ITEM,
    }

    def __init__(
        self,
        *,
        max_scan_page: int,
        max_continuation_page_gap: int = 1,
    ) -> None:
        self.max_scan_page = max_scan_page
        self.max_continuation_page_gap = max_continuation_page_gap

    def collect(
        self,
        elements: list[CanonicalElement],
        *,
        anchor_page: int,
        anchor_order: int | None,
    ) -> list[CanonicalElement]:
        accepted: list[CanonicalElement] = []
        last_toc_page: int | None = None

        for element in sorted(elements, key=lambda item: item.order_index):
            page_no = element.page_start or element.page_end
            if page_no is None or page_no < anchor_page or page_no > self.max_scan_page:
                continue

            if (
                anchor_order is not None
                and page_no == anchor_page
                and element.order_index <= anchor_order
            ):
                continue

            if element.element_type not in self._TOC_ELEMENT_TYPES:
                continue

            entries = TocEntryParser.extract_entries_from_element(element)
            if not entries:
                if (
                    accepted
                    and last_toc_page is not None
                    and page_no > last_toc_page + self.max_continuation_page_gap
                ):
                    break
                continue

            if (
                last_toc_page is not None
                and page_no > last_toc_page + self.max_continuation_page_gap
            ):
                break

            accepted.append(element)
            last_toc_page = page_no

        return accepted
