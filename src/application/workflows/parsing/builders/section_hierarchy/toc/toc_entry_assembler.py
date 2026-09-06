import re
from collections import defaultdict

from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    extract_heading_number,
    numbering_depth,
    strip_heading_number,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry import (
    TocEntry,
    normalize_toc_title,
)
from src.application.workflows.parsing.builders.section_hierarchy.toc.toc_entry_parser import (
    TocEntryParser,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)
from src.application.workflows.parsing.parsed_canonical_element import (
    ParsedCanonicalElement,
)


class TocEntryAssembler:
    """Assembles TOC entries across adjacent elements on each visual page."""

    def assemble(
        self,
        elements: list[ParsedCanonicalElement],
    ) -> list[TocEntry]:
        by_page: dict[int, list[ParsedCanonicalElement]] = defaultdict(list)
        for element in sorted(elements, key=lambda item: item.order_index):
            page_no = element.page_start or element.page_end
            if page_no is not None:
                by_page[page_no].append(element)

        entries: list[TocEntry] = []
        for page_no in sorted(by_page):
            entries.extend(self._assemble_page(by_page[page_no]))
        return self._deduplicate(entries)

    def _assemble_page(
        self,
        elements: list[ParsedCanonicalElement],
    ) -> list[TocEntry]:
        entries: list[TocEntry] = []
        numbered_title_fragments: list[str] = []

        for element in elements:
            parsed = TocEntryParser.extract_entries_from_element(element)
            if not parsed:
                fragment = self._numbered_title_fragment(element.text)
                if fragment:
                    numbered_title_fragments.append(fragment)
                continue
            entries.extend(parsed)

        return self._join_numbered_title_fragments(
            entries,
            numbered_title_fragments,
        )

    @classmethod
    def _join_numbered_title_fragments(
        cls,
        entries: list[TocEntry],
        fragments: list[str],
    ) -> list[TocEntry]:
        result = list(entries)
        unnumbered_indexes = [
            index
            for index, entry in enumerate(result)
            if entry.numbering is None
        ]
        for fragment, entry_index in zip(fragments, unnumbered_indexes):
            result[entry_index] = cls._merge_pending_title(
                fragment,
                result[entry_index],
            )
        return result

    @staticmethod
    def _numbered_title_fragment(value: str | None) -> str | None:
        text = re.sub(
            r"\s+",
            " ",
            repair_docling_text(str(value or "")).strip(),
        )
        if not text or extract_heading_number(text) is None:
            return None
        if re.search(r"\s\d{1,4}$", text):
            return None
        return text

    @staticmethod
    def _merge_pending_title(pending: str, entry: TocEntry) -> TocEntry:
        number = extract_heading_number(pending)
        title = " ".join(
            part
            for part in (strip_heading_number(pending), entry.title)
            if part
        )
        return TocEntry(
            title=title,
            normalized_title=normalize_toc_title(title),
            start_page=entry.start_page,
            level_hint=numbering_depth(number) or entry.level_hint,
            numbering=number,
        )

    @staticmethod
    def _deduplicate(entries: list[TocEntry]) -> list[TocEntry]:
        seen: set[tuple[str | None, str, int]] = set()
        result: list[TocEntry] = []
        for entry in entries:
            signature = (
                entry.numbering,
                entry.normalized_title,
                entry.start_page,
            )
            if signature in seen:
                continue
            seen.add(signature)
            result.append(entry)
        return result
