from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    extract_contextual_number,
    extract_heading_number,
    numbering_depth,
)
from src.application.workflows.parsing.builders.section_hierarchy.strategies.section_hierarchy_strategy import (
    SectionHierarchyStrategy,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry import (
    TocEntry,
    TocOutline,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_candidate_collector import (
    TocCandidateCollector,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry_parser import (
    TocEntryParser,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry_assembler import (
    TocEntryAssembler,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_header_matcher import (
    TocHeaderMatcher,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_heading_recognizer import (
    TocHeadingRecognizer,
)
from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.domain.common import ElementType


class TocPageRangeStrategy(SectionHierarchyStrategy):
    name = "toc_page_range"
    _TOC_ANCHOR_SCAN_PAGE_LIMIT = 20
    _TOC_MAX_SPAN_PAGES = 24

    def __init__(self) -> None:
        self._candidate_collector = TocCandidateCollector(
            max_span_pages=self._TOC_MAX_SPAN_PAGES
        )
        self._entry_assembler = TocEntryAssembler()

    def can_apply(
        self,
        headers: list[ParsedCanonicalElement],
        elements: list[ParsedCanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> bool:
        del current_levels
        outline = self.build_outline(headers, elements)
        return bool(outline.entries)

    def assign_levels(
        self,
        headers: list[ParsedCanonicalElement],
        elements: list[ParsedCanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> dict[str, int]:
        del current_levels

        sorted_headers = sorted(headers, key=lambda header: header.order_index)
        outline = self.build_outline(sorted_headers, elements)
        return self.assign_levels_from_outline(sorted_headers, outline)

    def assign_levels_from_outline(
        self,
        headers: list[ParsedCanonicalElement],
        outline: TocOutline,
    ) -> dict[str, int]:
        sorted_headers = sorted(headers, key=lambda header: header.order_index)
        if not outline.entries:
            return {}

        levels: dict[str, int] = {}
        if outline.toc_header_id:
            levels[outline.toc_header_id] = 1

        matched_roots: list[tuple[int, str]] = []
        for header in sorted_headers:
            entry = outline.matched_entries.get(header.element_id)
            if entry is None:
                continue

            levels[header.element_id] = entry.level_hint
            if entry.numbering:
                outline.header_numberings.setdefault(header.element_id, entry.numbering)

            page_no = header.page_start or header.page_end
            if page_no is not None and entry.level_hint == 1:
                matched_roots.append((page_no, header.element_id))

        matched_roots.sort(key=lambda value: value[0])
        matched_root_ranges = [
            (
                page_no,
                element_id,
                matched_roots[index + 1][0] if index + 1 < len(matched_roots) else None,
            )
            for index, (page_no, element_id) in enumerate(matched_roots)
        ]

        for header in sorted_headers:
            if header.element_id in levels:
                continue

            page_no = header.page_start or header.page_end
            if page_no is None:
                continue

            for start_page, _, next_page in matched_root_ranges:
                in_range = page_no >= start_page and (next_page is None or page_no < next_page)
                if not in_range:
                    continue

                inferred_level = self._infer_in_range_level(header)
                levels[header.element_id] = inferred_level
                break

        return levels

    def build_outline(
        self,
        headers: list[ParsedCanonicalElement],
        elements: list[ParsedCanonicalElement],
    ) -> TocOutline:
        anchor_page, toc_header_id, anchor_order = self._find_toc_anchor(headers, elements)
        if anchor_page is None:
            return TocOutline()

        candidate_elements = self._candidate_collector.collect(
            elements,
            anchor_page=anchor_page,
            anchor_order=anchor_order,
        )

        entries = self._entry_assembler.assemble(candidate_elements)

        if not entries:
            return TocOutline(toc_header_id=toc_header_id, entries=entries)

        matched_entries: dict[str, TocEntry] = {}
        header_numberings: dict[str, str] = {}
        unmatched_entries: list[TocEntry] = []
        matched_header_ids: set[str] = set()
        for entry in entries:
            header = TocHeaderMatcher.match_entry_to_header(entry, headers, matched_header_ids)
            if header is None:
                unmatched_entries.append(entry)
                continue

            matched_header_ids.add(header.element_id)
            matched_entries[header.element_id] = entry
            if entry.numbering:
                header_numberings[header.element_id] = entry.numbering

        return TocOutline(
            toc_header_id=toc_header_id,
            entries=entries,
            matched_entries=matched_entries,
            header_numberings=header_numberings,
            unmatched_entries=unmatched_entries,
        )

    def _find_toc_anchor(
        self,
        headers: list[ParsedCanonicalElement],
        elements: list[ParsedCanonicalElement],
    ) -> tuple[int | None, str | None, int | None]:
        for header in sorted(headers, key=lambda item: item.order_index):
            if not self._looks_like_toc_header(header.text):
                continue

            page_no = header.page_start or header.page_end
            if page_no is None or page_no > self._TOC_ANCHOR_SCAN_PAGE_LIMIT:
                continue

            return page_no, header.element_id, header.order_index

        early_tables = []

        for element in sorted(elements, key=lambda item: item.order_index):
            if element.element_type != ElementType.TABLE:
                continue

            if not self._is_document_index(element):
                continue

            page_no = element.page_start or element.page_end
            if page_no is None:
                continue

            if page_no > self._TOC_ANCHOR_SCAN_PAGE_LIMIT:
                continue

            early_tables.append(element)
        if not early_tables:
            return None, None, None

        for table in early_tables:
            if len(TocEntryParser.extract_entries_from_element(table)) >= 2:
                page_no = table.page_start or table.page_end
                return page_no, None, table.order_index

        return None, None, None

    @classmethod
    def _looks_like_toc_header(cls, value: str | None) -> bool:
        return TocHeadingRecognizer.matches(value)

    @staticmethod
    def _is_document_index(element: ParsedCanonicalElement) -> bool:
        return element.metadata.get("item_label") == "document_index"

    @staticmethod
    def _infer_in_range_level(header: ParsedCanonicalElement) -> int:
        number = extract_heading_number(header.text)
        depth = numbering_depth(number)
        if depth is not None:
            return depth

        contextual_number = extract_contextual_number(header.text)
        contextual_depth = numbering_depth(contextual_number)
        if contextual_depth is not None:
            return min(contextual_depth + 1, 6)

        return 2
