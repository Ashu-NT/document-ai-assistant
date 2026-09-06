from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from statistics import median

from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    extract_heading_number,
    numbering_depth,
    strip_heading_number,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc import TocOutline
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry import (
    normalize_toc_title,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)
from src.domain.common import ElementType


@dataclass(slots=True)
class HeadingCandidateDocumentContext:
    headers: tuple[ParsedCanonicalElement, ...]
    elements: tuple[ParsedCanonicalElement, ...]
    toc_outline: TocOutline | None
    numberings: dict[str, str]
    normalized_titles: dict[str, str]
    title_counts: Counter[str]
    element_positions: dict[str, int]
    median_header_height: float | None

    @classmethod
    def build(
        cls,
        *,
        headers: list[ParsedCanonicalElement],
        elements: list[ParsedCanonicalElement],
        toc_outline: TocOutline | None,
        numberings: dict[str, str],
    ) -> "HeadingCandidateDocumentContext":
        ordered_headers = tuple(sorted(headers, key=lambda item: item.order_index))
        ordered_elements = tuple(sorted(elements, key=lambda item: item.order_index))
        normalized_titles = {
            header.element_id: normalize_toc_title(strip_heading_number(header.text))
            for header in ordered_headers
        }
        heights = [
            abs(header.bbox.y2 - header.bbox.y1)
            for header in ordered_headers
            if header.bbox is not None and abs(header.bbox.y2 - header.bbox.y1) > 0
        ]
        return cls(
            headers=ordered_headers,
            elements=ordered_elements,
            toc_outline=toc_outline,
            numberings=dict(numberings),
            normalized_titles=normalized_titles,
            title_counts=Counter(normalized_titles.values()),
            element_positions={
                element.element_id: index
                for index, element in enumerate(ordered_elements)
            },
            median_header_height=median(heights) if heights else None,
        )

    def next_content(
        self,
        header: ParsedCanonicalElement,
    ) -> ParsedCanonicalElement | None:
        position = self.element_positions.get(header.element_id)
        if position is None:
            return None
        for candidate_position in range(position + 1, len(self.elements)):
            element = self.elements[candidate_position]
            if element.element_type == ElementType.SECTION_HEADER:
                return None
            if element.text or element.element_type in {
                ElementType.TABLE,
                ElementType.PICTURE,
                ElementType.FORM,
            }:
                return element
        return None

    def has_nearby_element_type(
        self,
        header: ParsedCanonicalElement,
        element_type: ElementType,
        *,
        max_order_gap: int = 4,
    ) -> bool:
        """Finds local structural evidence without crossing a heading or page boundary."""
        position = self.element_positions.get(header.element_id)
        if position is None:
            return False
        header_page = header.page_start or header.page_end
        for element in self.elements[position + 1 : position + max_order_gap + 1]:
            if element.element_type == ElementType.SECTION_HEADER:
                break
            element_page = element.page_start or element.page_end
            if (
                header_page is not None
                and element_page is not None
                and element_page != header_page
            ):
                break
            if element.element_type == element_type:
                return True
        return False

    def has_descendant_pattern(self, header_index: int) -> bool:
        header = self.headers[header_index]
        numbering = self.numberings.get(header.element_id)
        if not numbering:
            return False
        page = header.page_start or header.page_end
        for candidate in self.headers[header_index + 1 : header_index + 9]:
            candidate_page = candidate.page_start or candidate.page_end
            if page is not None and candidate_page is not None and candidate_page - page > 3:
                break
            candidate_number = self.numberings.get(candidate.element_id)
            if candidate_number and candidate_number.startswith(f"{numbering}."):
                return True
        return False

    def has_sibling_pattern(self, header_index: int) -> bool:
        numbering = self.numberings.get(self.headers[header_index].element_id)
        if not numbering:
            return False
        for candidate_index in (header_index - 1, header_index + 1):
            if not 0 <= candidate_index < len(self.headers):
                continue
            candidate_number = self.numberings.get(
                self.headers[candidate_index].element_id
            )
            if self._are_numbered_siblings(numbering, candidate_number):
                return True
        return False

    @staticmethod
    def _are_numbered_siblings(left: str, right: str | None) -> bool:
        if not right or numbering_depth(left) != numbering_depth(right):
            return False
        left_parts = left.split(".")
        right_parts = right.split(".")
        if left_parts[:-1] != right_parts[:-1]:
            return False
        try:
            return abs(int(left_parts[-1]) - int(right_parts[-1])) == 1
        except ValueError:
            return False

    def toc_entry_for(self, header_id: str):
        if self.toc_outline is None:
            return None
        return self.toc_outline.matched_entries.get(header_id)

    def normalized_title(self, header_id: str) -> str:
        return self.normalized_titles.get(header_id, "")

    def repeated_title_count(self, header_id: str) -> int:
        return self.title_counts[self.normalized_title(header_id)]

    def has_nearby_repeated_title(
        self,
        header_index: int,
        *,
        max_page_distance: int = 2,
        max_header_distance: int = 80,
    ) -> bool:
        header = self.headers[header_index]
        title = self.normalized_title(header.element_id)
        if not title or self.title_counts[title] < 2:
            return False
        page = header.page_start or header.page_end
        start = max(0, header_index - max_header_distance)
        stop = min(len(self.headers), header_index + max_header_distance + 1)
        for candidate_index in range(start, stop):
            if candidate_index == header_index:
                continue
            candidate = self.headers[candidate_index]
            if self.normalized_title(candidate.element_id) != title:
                continue
            candidate_page = candidate.page_start or candidate.page_end
            if page is None or candidate_page is None:
                return True
            if abs(candidate_page - page) <= max_page_distance:
                return True
        return False

    def has_prominent_height(self, header: ParsedCanonicalElement) -> bool:
        if header.bbox is None or not self.median_header_height:
            return False
        height = abs(header.bbox.y2 - header.bbox.y1)
        return height >= self.median_header_height * 1.2

    def numbering_for(self, header: ParsedCanonicalElement) -> str | None:
        return self.numberings.get(header.element_id) or extract_heading_number(
            header.text
        )
