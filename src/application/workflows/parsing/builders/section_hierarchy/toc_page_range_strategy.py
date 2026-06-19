import re
from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    extract_contextual_number,
    extract_heading_number,
    numbering_depth,
    strip_heading_number,
)
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
    level_hint: int
    numbering: str | None = None


@dataclass(slots=True)
class TocOutline:
    toc_header_id: str | None = None
    entries: list[TocEntry] = field(default_factory=list)
    matched_entries: dict[str, TocEntry] = field(default_factory=dict)
    header_numberings: dict[str, str] = field(default_factory=dict)


class TocPageRangeStrategy(SectionHierarchyStrategy):
    name = "toc_page_range"
    _TOC_HEADER_ALIASES = {
        "contents",
        "content",
        "table of contents",
        "inhaltsverzeichnis",
        "inhalt",
        "sommaire",
        "toc",
    }
    _TOC_SCAN_PAGE_LIMIT = 8
    _TOC_SCAN_SPAN = 3

    def can_apply(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> bool:
        del current_levels
        outline = self.build_outline(headers, elements)
        return bool(outline.entries)

    def assign_levels(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
        current_levels: dict[str, int] | None = None,
    ) -> dict[str, int]:
        del current_levels

        sorted_headers = sorted(headers, key=lambda header: header.order_index)
        outline = self.build_outline(sorted_headers, elements)
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
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
    ) -> TocOutline:
        anchor_page, toc_header_id, anchor_order = self._find_toc_anchor(headers, elements)
        if anchor_page is None:
            return TocOutline()

        candidate_elements = [
            element
            for element in sorted(elements, key=lambda item: item.order_index)
            if self._is_toc_candidate_element(
                element,
                anchor_page=anchor_page,
                anchor_order=anchor_order,
            )
        ]

        entries: list[TocEntry] = []
        for element in candidate_elements:
            entries.extend(self._extract_entries_from_element(element))

        if not entries:
            return TocOutline(toc_header_id=toc_header_id, entries=entries)

        matched_entries: dict[str, TocEntry] = {}
        header_numberings: dict[str, str] = {}
        matched_header_ids: set[str] = set()
        for entry in entries:
            header = self._match_toc_entry_to_header(entry, headers, matched_header_ids)
            if header is None:
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
        )

    def _find_toc_anchor(
        self,
        headers: list[CanonicalElement],
        elements: list[CanonicalElement],
    ) -> tuple[int | None, str | None, int | None]:
        for header in sorted(headers, key=lambda item: item.order_index):
            if not self._looks_like_toc_header(header.text):
                continue

            page_no = header.page_start or header.page_end
            if page_no is None:
                continue

            return page_no, header.element_id, header.order_index

        early_tables = [
            element
            for element in sorted(elements, key=lambda item: item.order_index)
            if element.element_type == ElementType.TABLE
            and self._is_document_index(element)
            and (element.page_start or element.page_end or 0) <= self._TOC_SCAN_PAGE_LIMIT
        ]
        if not early_tables:
            return None, None, None

        for table in early_tables:
            if len(self._extract_entries_from_element(table)) >= 2:
                page_no = table.page_start or table.page_end
                return page_no, None, table.order_index

        return None, None, None

    def _is_toc_candidate_element(
        self,
        element: CanonicalElement,
        *,
        anchor_page: int,
        anchor_order: int | None,
    ) -> bool:
        page_no = element.page_start or element.page_end
        if page_no is None:
            return False

        if page_no < anchor_page or page_no >= anchor_page + self._TOC_SCAN_SPAN:
            return False

        if (
            anchor_order is not None
            and page_no == anchor_page
            and element.order_index <= anchor_order
        ):
            return False

        return element.element_type in {
            ElementType.TABLE,
            ElementType.TEXT,
            ElementType.LIST_ITEM,
        }

    def _extract_entries_from_element(
        self,
        element: CanonicalElement,
    ) -> list[TocEntry]:
        rows = element.metadata.get("table_rows")
        if isinstance(rows, list):
            entries = self._parse_toc_rows(rows)
            if entries:
                return entries

        text = element.text or element.metadata.get("markdown")
        if not text:
            return []

        return self._parse_toc_text(text)

    def _parse_toc_rows(self, rows: list[object]) -> list[TocEntry]:
        entries: list[TocEntry] = []
        for row in rows:
            if not isinstance(row, list):
                continue

            cells = [self._clean_cell(cell) for cell in row]
            if not any(cells):
                continue

            page_index, page_no = self._extract_row_page(cells)
            if page_index is None or page_no is None:
                continue

            content_cells = [
                cell
                for index, cell in enumerate(cells)
                if index != page_index and cell
            ]
            if not content_cells:
                continue

            numbering: str | None = None
            title_parts: list[str] = []
            for cell in content_cells:
                exact_number = self._extract_exact_number(cell)
                if exact_number is not None and numbering is None:
                    numbering = exact_number
                    continue

                combined_number, combined_title = self._split_number_and_title(cell)
                if combined_number is not None and numbering is None:
                    numbering = combined_number
                    if combined_title:
                        title_parts.append(combined_title)
                    continue

                title_parts.append(cell)

            title = self._clean_toc_title(" ".join(self._dedupe_consecutive(title_parts)))
            if not title:
                continue

            level_hint = numbering_depth(numbering)
            if level_hint is None:
                first_content_index = min(
                    index
                    for index, cell in enumerate(cells)
                    if cell and index != page_index
                )
                level_hint = max(1, first_content_index + 1)

            entries.append(
                TocEntry(
                    title=title,
                    normalized_title=self._normalize_title(title),
                    start_page=page_no,
                    level_hint=level_hint,
                    numbering=numbering,
                )
            )

        return entries

    def _parse_toc_text(self, text: str) -> list[TocEntry]:
        entries: list[TocEntry] = []
        for raw_line in text.splitlines():
            line = raw_line.strip().strip("|").strip()
            if not line or set(line) <= {"-", ":", "|"}:
                continue

            line = re.sub(r"\s+", " ", line)
            match = re.match(r"^(?P<title>.+?)\.{2,}\s*(?P<page>\d+)$", line)
            if match is None:
                match = re.match(r"^(?P<title>.+?)\s+(?P<page>\d+)$", line)
            if match is None:
                continue

            title_text = self._clean_toc_title(match.group("title"))
            if not title_text:
                continue

            numbering, title = self._split_number_and_title(title_text)
            normalized_title = self._normalize_title(title or title_text)
            if not normalized_title:
                continue

            entries.append(
                TocEntry(
                    title=title or title_text,
                    normalized_title=normalized_title,
                    start_page=int(match.group("page")),
                    level_hint=numbering_depth(numbering) or 1,
                    numbering=numbering,
                )
            )

        return entries

    def _match_toc_entry_to_header(
        self,
        entry: TocEntry,
        headers: list[CanonicalElement],
        matched_header_ids: set[str],
    ) -> CanonicalElement | None:
        candidates = [
            header
            for header in headers
            if header.element_id not in matched_header_ids
        ]

        for candidate in candidates:
            candidate_number = extract_heading_number(candidate.text)
            candidate_title = self._normalize_title(strip_heading_number(candidate.text))
            if (
                entry.numbering
                and candidate_number == entry.numbering
                and candidate_title == entry.normalized_title
            ):
                return candidate

        for candidate in candidates:
            candidate_title = self._normalize_title(strip_heading_number(candidate.text))
            if candidate_title == entry.normalized_title:
                return candidate

        for candidate in candidates:
            candidate_title = self._normalize_title(strip_heading_number(candidate.text))
            if (
                candidate_title
                and (
                    candidate_title in entry.normalized_title
                    or entry.normalized_title in candidate_title
                )
            ):
                return candidate

        return None

    @classmethod
    def _looks_like_toc_header(cls, value: str | None) -> bool:
        return cls._normalize_title(value) in cls._TOC_HEADER_ALIASES

    @staticmethod
    def _is_document_index(element: CanonicalElement) -> bool:
        return element.metadata.get("item_label") == "document_index"

    @staticmethod
    def _infer_in_range_level(header: CanonicalElement) -> int:
        number = extract_heading_number(header.text)
        depth = numbering_depth(number)
        if depth is not None:
            return depth

        contextual_number = extract_contextual_number(header.text)
        contextual_depth = numbering_depth(contextual_number)
        if contextual_depth is not None:
            return min(contextual_depth + 1, 6)

        return 2

    @staticmethod
    def _extract_row_page(cells: list[str]) -> tuple[int | None, int | None]:
        for index in range(len(cells) - 1, -1, -1):
            cell = cells[index]
            if not cell:
                continue

            if re.fullmatch(r"\d{1,4}", cell):
                return index, int(cell)

        return None, None

    @staticmethod
    def _extract_exact_number(value: str) -> str | None:
        match = re.fullmatch(r"(\d+(?:\.\d+)*)", value.strip())
        if match is None:
            return None

        return match.group(1)

    @staticmethod
    def _split_number_and_title(value: str) -> tuple[str | None, str | None]:
        stripped = value.strip()
        match = re.match(
            r"^(?P<number>\d+(?:\.\d+)*)\s+(?P<title>.+)$",
            stripped,
        )
        if match is None:
            return None, stripped or None

        return match.group("number"), match.group("title").strip(" .")

    @staticmethod
    def _clean_cell(value: object) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip())

    @staticmethod
    def _dedupe_consecutive(values: list[str]) -> list[str]:
        deduped: list[str] = []
        for value in values:
            if not value:
                continue
            if deduped and deduped[-1] == value:
                continue
            deduped.append(value)
        return deduped

    @staticmethod
    def _clean_toc_title(value: str | None) -> str:
        if not value:
            return ""

        text = re.sub(r"\.{2,}", " ", value)
        text = re.sub(r"\s+", " ", text)
        return text.strip(" .|-")

    @staticmethod
    def _normalize_title(value: str | None) -> str:
        if not value:
            return ""

        text = value.casefold()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
