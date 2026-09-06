from collections import defaultdict

from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry_parser import (
    TocEntryParser,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_element_eligibility_policy import (
    TocElementEligibilityPolicy,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
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
        max_span_pages: int = 24,
        max_continuation_page_gap: int = 1,
    ) -> None:
        self.max_span_pages = max(1, max_span_pages)
        self.max_continuation_page_gap = max(0, max_continuation_page_gap)

    def collect(
        self,
        elements: list[ParsedCanonicalElement],
        *,
        anchor_page: int,
        anchor_order: int | None,
    ) -> list[ParsedCanonicalElement]:
        by_page: dict[int, list[ParsedCanonicalElement]] = defaultdict(list)
        last_page = anchor_page + self.max_span_pages - 1
        for element in sorted(elements, key=lambda item: item.order_index):
            page_no = element.page_start or element.page_end
            if page_no is None or not anchor_page <= page_no <= last_page:
                continue
            if (
                anchor_order is not None
                and page_no == anchor_page
                and element.order_index <= anchor_order
            ):
                continue
            if element.element_type in self._TOC_ELEMENT_TYPES:
                if not TocElementEligibilityPolicy.is_eligible(element):
                    continue
                by_page[page_no].append(element)

        accepted: list[ParsedCanonicalElement] = []
        last_evidence_page: int | None = None
        for page_no in sorted(by_page):
            page_elements = by_page[page_no]
            if not self._page_has_toc_evidence(page_elements):
                if (
                    last_evidence_page is not None
                    and page_no > last_evidence_page + self.max_continuation_page_gap
                ):
                    break
                continue
            if (
                last_evidence_page is not None
                and page_no > last_evidence_page + self.max_continuation_page_gap + 1
            ):
                break
            accepted.extend(page_elements)
            last_evidence_page = page_no

        return accepted

    @staticmethod
    def _page_has_toc_evidence(
        elements: list[ParsedCanonicalElement],
    ) -> bool:
        for element in elements:
            if element.metadata.get("item_label") == "document_index":
                return True
            if TocEntryParser.extract_entries_from_element(element):
                return True
        return False
