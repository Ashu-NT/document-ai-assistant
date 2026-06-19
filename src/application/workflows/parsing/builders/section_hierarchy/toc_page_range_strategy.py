import re
from dataclasses import dataclass

from src.application.workflows.parsing.builders.section_hierarchy.section_hierarchy_strategy import (
    SectionHierarchyStrategy,
)
from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.domain.common import ElementType


@dataclass(slots=True)
class TocEntry:
    title: str
    normalized_title: str
    start_page: int


class TocPageRangeStrategy(SectionHierarchyStrategy):
    name = "toc_page_range"

    def can_apply(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> bool:
        del current_levels
        entries = self._extract_toc_entries(headers, elements)
        return bool(entries)

    def assign_levels(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> dict[str, int]:
        del current_levels

        sorted_headers = sorted(headers, key=lambda header: header.order_index)
        entries = self._extract_toc_entries(sorted_headers, elements)
        if not entries:
            return {}

        toc_header_id = self._find_toc_header_id(sorted_headers)
        levels: dict[str, int] = {}
        matched_root_ids: set[str] = set()
        headers_by_title = self._group_headers_by_title(sorted_headers)

        if toc_header_id:
            levels[toc_header_id] = 1

        matched_roots: list[tuple[int, str]] = []
        for entry in entries:
            header = self._match_toc_entry_to_header(entry, headers_by_title, matched_root_ids)
            if header is None:
                continue

            matched_root_ids.add(header.element_id)
            levels[header.element_id] = 1
            if header.page_start is not None:
                matched_roots.append((header.page_start, header.element_id))

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

            for start_page, root_header_id, next_page in matched_root_ranges:
                in_range = page_no >= start_page and (next_page is None or page_no < next_page)
                if not in_range:
                    continue

                if header.element_id == root_header_id:
                    levels[header.element_id] = 1
                else:
                    levels[header.element_id] = 2
                break

        return levels

    def _extract_toc_entries(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
    ) -> list[TocEntry]:
        toc_header = self._find_toc_header(headers)
        if toc_header is None:
            return []

        candidate_elements = [
            element
            for element in sorted(elements, key=lambda item: item.order_index)
            if (element.page_start or element.page_end) == (toc_header.page_start or toc_header.page_end)
            and element.order_index > toc_header.order_index
            and element.element_type in {ElementType.TABLE, ElementType.TEXT, ElementType.LIST_ITEM}
        ]

        entries: list[TocEntry] = []
        for element in candidate_elements:
            text = element.text or element.metadata.get("markdown")
            if not text:
                continue

            entries.extend(self._parse_toc_entries(text))

        return entries

    @staticmethod
    def _parse_toc_entries(text: str) -> list[TocEntry]:
        entries: list[TocEntry] = []
        for raw_line in text.splitlines():
            line = raw_line.strip().strip("|").strip()
            if not line:
                continue

            if set(line) <= {"-", ":", "|"}:
                continue

            line = re.sub(r"\s+", " ", line)
            match = re.match(r"^(?P<title>.+?)\.{2,}\s*(?P<page>\d+)$", line)
            if match is None:
                match = re.match(r"^(?P<title>.+?)\s+(?P<page>\d+)$", line)
            if match is None:
                continue

            title = match.group("title").strip(" .")
            if not title:
                continue

            page_no = int(match.group("page"))
            entries.append(
                TocEntry(
                    title=title,
                    normalized_title=TocPageRangeStrategy._normalize_title(title),
                    start_page=page_no,
                )
            )

        return entries

    @staticmethod
    def _group_headers_by_title(
        headers: list[CanonicalElement],
    ) -> dict[str, list[CanonicalElement]]:
        grouped: dict[str, list[CanonicalElement]] = {}

        for header in headers:
            if not header.text:
                continue

            grouped.setdefault(
                TocPageRangeStrategy._normalize_title(header.text),
                [],
            ).append(header)

        return grouped

    @staticmethod
    def _match_toc_entry_to_header(
        entry: TocEntry,
        headers_by_title: dict[str, list[CanonicalElement]],
        matched_root_ids: set[str],
    ) -> CanonicalElement | None:
        for candidate in headers_by_title.get(entry.normalized_title, []):
            if candidate.element_id not in matched_root_ids:
                return candidate

        for normalized_title, candidates in headers_by_title.items():
            if normalized_title in entry.normalized_title or entry.normalized_title in normalized_title:
                for candidate in candidates:
                    if candidate.element_id not in matched_root_ids:
                        return candidate

        return None

    @staticmethod
    def _find_toc_header(headers: list[CanonicalElement]) -> CanonicalElement | None:
        for header in headers:
            if TocPageRangeStrategy._normalize_title(header.text) == "table of contents":
                return header

        return None

    @classmethod
    def _find_toc_header_id(cls, headers: list[CanonicalElement]) -> str | None:
        toc_header = cls._find_toc_header(headers)
        return toc_header.element_id if toc_header is not None else None

    @staticmethod
    def _normalize_title(value: str | None) -> str:
        if not value:
            return ""

        text = value.casefold()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
