from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry import (
    TocEntry,
)
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


class TocVisualLineAssembler:
    """Rebuilds bbox-aligned TOC rows split into independent text items."""

    _LINE_TOLERANCE = 3.0
    _TEXT_TYPES = {ElementType.TEXT, ElementType.LIST_ITEM}

    def assemble(self, elements: list[ParsedCanonicalElement]) -> list[TocEntry]:
        lines_by_page: dict[int | None, list[list[ParsedCanonicalElement]]] = {}
        for element in sorted(elements, key=self._vertical_sort_key):
            if element.element_type not in self._TEXT_TYPES or element.bbox is None:
                continue
            if not TocElementEligibilityPolicy.is_eligible(element):
                continue
            page_lines = lines_by_page.setdefault(element.page_start, [])
            center_y = self._center_y(element)
            matching_line = next(
                (
                    line
                    for line in page_lines
                    if abs(self._center_y(line[0]) - center_y) <= self._LINE_TOLERANCE
                ),
                None,
            )
            if matching_line is None:
                page_lines.append([element])
            else:
                matching_line.append(element)

        entries: list[TocEntry] = []
        for page_lines in lines_by_page.values():
            for line in page_lines:
                entries.extend(self._parse_line(line))
        return entries

    @staticmethod
    def _parse_line(elements: list[ParsedCanonicalElement]) -> list[TocEntry]:
        ordered = sorted(
            elements,
            key=lambda element: element.bbox.x1 if element.bbox is not None else 0.0,
        )
        segments: list[str] = []
        current: list[str] = []
        for element in ordered:
            text = " ".join(str(element.text or "").split())
            if not text:
                continue
            current.append(text)
            if text.isdigit() and any(not value.replace(".", "").isdigit() for value in current[:-1]):
                segments.append(" ".join(current))
                current = []

        entries: list[TocEntry] = []
        for segment in segments:
            entries.extend(TocEntryParser.parse_toc_text(segment))
        return entries

    @staticmethod
    def _vertical_sort_key(element: ParsedCanonicalElement) -> tuple[float, float]:
        if element.bbox is None:
            return (0.0, 0.0)
        return (-TocVisualLineAssembler._center_y(element), element.bbox.x1)

    @staticmethod
    def _center_y(element: ParsedCanonicalElement) -> float:
        bbox = element.bbox
        if bbox is None:
            return 0.0
        return (bbox.y1 + bbox.y2) / 2.0
