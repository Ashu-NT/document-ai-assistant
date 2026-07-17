from __future__ import annotations

import re
from dataclasses import dataclass

from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    extract_heading_number,
    strip_heading_number,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)

TOC_PAGE_NUMBER_PATTERN = re.compile(r"\d{1,4}")
# A table's dotted leader ("......") between title and page number commonly
# gets split across two adjacent cells at an arbitrary point, leaving a few
# residual leader dots stuck to the page-number cell (e.g. "..18" instead of
# a clean "18"). Dots are never part of a real page number in this context,
# so they're safe to strip before checking whether a cell is a page number.
_ROW_PAGE_CELL_PATTERN = re.compile(r"^\.*\s*(?P<page>\d{1,4})\s*\.*$")


@dataclass(frozen=True, slots=True)
class _ParsedTocEntry:
    numbering: str
    title: str
    page: int
    used_dot_leader: bool


class DoclingTocTableRowReconstructor:
    _DOT_LEADER_PATTERN = re.compile(r"^(?P<title>.+?)\.{2,}\s*(?P<page>\d+)$")
    _SPACE_PAGE_PATTERN = re.compile(r"^(?P<title>.+?)\s+(?P<page>\d+)$")
    _ALPHA_TOKEN_PATTERN = re.compile(r"[A-Za-z]+")

    def reconstruct(self, rows: list[list[str]]) -> list[list[str]]:
        parsed_rows = self._parse_rows(rows)
        if len(parsed_rows) < 3:
            return rows

        row_entry_count = sum(
            1
            for row in rows
            if self._parse_row(row) is not None
        )
        minimum_expected = (
            max(3, row_entry_count)
            if row_entry_count >= 2
            else max(3, len(self._non_empty_cells(rows)) // 2)
        )
        if len(parsed_rows) < minimum_expected:
            return rows

        strong_match_count = sum(
            1
            for entry in parsed_rows
            if entry.numbering or entry.used_dot_leader
        )
        if strong_match_count < max(2, len(parsed_rows) // 2):
            return rows

        include_numbering = any(entry.numbering for entry in parsed_rows)
        header = (
            ["Number", "Title", "Page"]
            if include_numbering
            else ["Title", "Page"]
        )
        reconstructed = [header]
        for entry in parsed_rows:
            if include_numbering:
                reconstructed.append([entry.numbering, entry.title, str(entry.page)])
            else:
                reconstructed.append([entry.title, str(entry.page)])
        return reconstructed

    def _parse_rows(self, rows: list[list[str]]) -> list[_ParsedTocEntry]:
        parsed: list[_ParsedTocEntry] = []
        for row in rows:
            parsed_row = self._parse_row(row)
            if parsed_row is not None:
                parsed.append(parsed_row)
                continue
            row_entries: list[_ParsedTocEntry] = []
            for cell in row:
                row_entries.extend(self._parse_cell(cell))
            for entry in self._dedupe_row_entries(row_entries):
                parsed.append(entry)
        return parsed

    def _parse_row(self, row: list[str]) -> _ParsedTocEntry | None:
        cells = [self._clean_cell(cell) for cell in row if self._clean_cell(cell)]
        if len(cells) < 2:
            return None

        page_index, page_number = self._extract_row_page(cells)
        if page_index is None or page_number is None:
            return None

        numbering: str | None = None
        title_parts: list[str] = []
        for index, cell in enumerate(cells):
            if index == page_index:
                continue
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

        clean_title = self._clean_title(title_parts)
        if not clean_title:
            return None
        if numbering is None and not self._looks_like_root_toc_title(clean_title):
            return None
        return _ParsedTocEntry(
            numbering=numbering or "",
            title=clean_title,
            page=page_number,
            used_dot_leader=False,
        )

    def _parse_cell(self, cell: str) -> list[_ParsedTocEntry]:
        entry = self._parse_entry(cell)
        if entry is None:
            return []
        return [entry]

    def _parse_entry(self, value: str) -> _ParsedTocEntry | None:
        text = self._clean_cell(value)
        if not text:
            return None

        dot_leader_match = self._DOT_LEADER_PATTERN.match(text)
        match = dot_leader_match or self._SPACE_PAGE_PATTERN.match(text)
        if match is None:
            return None

        title = match.group("title").strip()
        page = int(match.group("page"))
        numbering = extract_heading_number(title) or ""
        clean_title = strip_heading_number(title).strip(" .|-")
        if not clean_title:
            return None
        if dot_leader_match is None and not (
            numbering or self._looks_like_root_toc_title(clean_title)
        ):
            return None
        return _ParsedTocEntry(
            numbering=numbering,
            title=clean_title,
            page=page,
            used_dot_leader=dot_leader_match is not None,
        )

    @staticmethod
    def _dedupe_row_entries(
        entries: list[_ParsedTocEntry],
    ) -> list[_ParsedTocEntry]:
        deduped: list[_ParsedTocEntry] = []
        seen: set[tuple[str, str, int]] = set()
        for entry in entries:
            key = (entry.numbering, entry.title, entry.page)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(entry)
        return deduped

    @staticmethod
    def _non_empty_cells(rows: list[list[str]]) -> list[str]:
        return [
            str(cell).strip()
            for row in rows
            for cell in row
            if str(cell).strip()
        ]

    @staticmethod
    def _clean_cell(value: object) -> str:
        return re.sub(
            r"\s+",
            " ",
            repair_docling_text(str(value or "")).strip().strip("|").strip(),
        )

    @staticmethod
    def _extract_row_page(cells: list[str]) -> tuple[int | None, int | None]:
        for index in range(len(cells) - 1, -1, -1):
            match = _ROW_PAGE_CELL_PATTERN.fullmatch(cells[index])
            if match:
                return index, int(match.group("page"))
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
        match = re.match(r"^(?P<number>\d+(?:\.\d+)*)\s+(?P<title>.+)$", stripped)
        if match is None:
            return None, stripped or None
        return match.group("number"), match.group("title").strip(" .")

    def _clean_title(self, title_parts: list[str]) -> str:
        title = " ".join(self._dedupe_row_entries_text(title_parts))
        return title.strip(" .|-")

    @staticmethod
    def _dedupe_row_entries_text(values: list[str]) -> list[str]:
        deduped: list[str] = []
        for value in values:
            if not value:
                continue
            if deduped and deduped[-1] == value:
                continue
            deduped.append(value)
        return deduped

    def _looks_like_root_toc_title(self, value: str) -> bool:
        if any(character.isdigit() for character in value):
            return False

        alpha_tokens = self._ALPHA_TOKEN_PATTERN.findall(value)
        return 1 <= len(alpha_tokens) <= 6
