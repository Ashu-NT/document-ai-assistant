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

# Page numbering isn't always Arabic-digit throughout a document -- a book's
# front matter commonly uses roman numerals ("i, ii, iii...") while the main
# body switches to "1, 2, 3...", and both conventions can appear in the same
# document (different TOC tables/pages). The lookahead requires at least one
# roman-numeral letter (M/D/C/L/X/V/I, either case) so this never matches an
# empty string, and the whole fragment enforces strict roman-numeral
# structure (proper subtractive-notation ordering), not just "any combination
# of these letters" -- e.g. "CIVIL"/"DID"/"LID" correctly do not match, since
# they don't fit the thousands-hundreds-tens-ones grouping. The one common
# English word that does still validly match is "mix" (a genuine, syntactically
# valid roman numeral reading), an accepted, narrow false-positive risk of the
# same order as this reconstructor's existing numeric/lettered-numbering
# false-positive risks -- and it only matters where a page-number-shaped
# candidate is expected (an isolated cell, or text immediately before a
# dot-leader/whitespace at the very end of a cell), not in arbitrary prose.
_ROMAN_NUMERAL_TEXT = (
    r"(?i:(?=[MDCLXVI])M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))"
)
_PAGE_REFERENCE_TEXT = rf"(?:\d{{1,4}}|{_ROMAN_NUMERAL_TEXT})"
TOC_PAGE_NUMBER_PATTERN = re.compile(_PAGE_REFERENCE_TEXT)
# A table's dotted leader ("......") between title and page number commonly
# gets split across two adjacent cells at an arbitrary point, leaving a few
# residual leader dots stuck to the page-number cell (e.g. "..18" instead of
# a clean "18"). Real-world extraction can also break one leader into several
# dot-runs with stray whitespace between them (e.g. "..... ..... 30"), so all
# whitespace is stripped from the candidate cell (see _extract_row_page)
# before this pattern is applied. Dots/whitespace are never part of a real
# page number in this context, so both are always safe to strip.
_ROW_PAGE_CELL_PATTERN = re.compile(rf"^\.*(?P<page>{_PAGE_REFERENCE_TEXT})\.*$")
# Numbering like "7.3" can come back from extraction with stray whitespace
# around the decimal point (e.g. "7 . 3", likely a font-kerning/glyph-spacing
# artifact) -- this never happens in real prose (a digit directly adjacent to
# ". " followed by another digit is not a natural English/German sentence
# shape), so collapsing it is safe and never affects genuine title text.
_SPACED_DECIMAL_PATTERN = re.compile(r"(\d)\s*\.\s*(\d)")
# TOC/section numbering isn't always purely numeric -- lettered appendices
# and annexes ("A", "B.2", "7.A") are a common, generic convention, not a
# one-off. A segment is either digits or a short (1-2 char) run of UPPERCASE
# letters -- deliberately not lowercase or longer runs, so this never matches
# an ordinary title word (e.g. "Overview"/"General" never fullmatch this,
# since real words mix case or run longer); the one accepted, low-probability
# false-positive case is a lone 1-2 letter all-caps abbreviation cell (e.g.
# "US"), which is rare and, if misread, is no worse than this reconstructor's
# existing numeric-only false-positive risk. Used only where numbering and
# title text are combined in one cell (_split_number_and_title) -- lowercase
# is deliberately excluded there, since short lowercase words ("of", "to",
# "in"...) are common at the start of ordinary two-word phrases and would
# otherwise misfire constantly.
_NUMBERING_SEGMENT = r"(?:\d+|[A-Z]{1,2})"
_NUMBERING_PATTERN_TEXT = rf"{_NUMBERING_SEGMENT}(?:\.{_NUMBERING_SEGMENT})*"
# Used only for a cell that IS the numbering and nothing else
# (_extract_exact_number) -- there, lowercase is safe to include too (a cell
# containing literally just "a" or "b", with no other text at all, is
# overwhelmingly likely to be genuine lettered numbering, not a coincidental
# lone short word).
_BARE_NUMBERING_SEGMENT = r"(?:\d+|[A-Za-z]{1,2})"
_BARE_NUMBERING_PATTERN_TEXT = (
    rf"{_BARE_NUMBERING_SEGMENT}(?:\.{_BARE_NUMBERING_SEGMENT})*"
)


@dataclass(frozen=True, slots=True)
class _ParsedTocEntry:
    numbering: str
    title: str
    # Kept as the original matched text (not int) so a roman-numeral page
    # reference (e.g. front-matter "iii") is never conflated with an Arabic
    # page sharing the same value elsewhere in the same document.
    page: str
    used_dot_leader: bool


class DoclingTocTableRowReconstructor:
    _DOT_LEADER_PATTERN = re.compile(
        rf"^(?P<title>.+?)\.{{2,}}\s*(?P<page>{_PAGE_REFERENCE_TEXT})$"
    )
    _SPACE_PAGE_PATTERN = re.compile(
        rf"^(?P<title>.+?)\s+(?P<page>{_PAGE_REFERENCE_TEXT})$"
    )
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
        page = match.group("page")
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
        seen: set[tuple[str, str, str]] = set()
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
        text = repair_docling_text(str(value or "")).strip().strip("|").strip()
        text = DoclingTocTableRowReconstructor._collapse_spaced_numbering(text)
        return re.sub(r"\s+", " ", text)

    @staticmethod
    def _collapse_spaced_numbering(value: str) -> str:
        previous = None
        current = value
        while previous != current:
            previous = current
            current = _SPACED_DECIMAL_PATTERN.sub(r"\1.\2", current)
        return current

    @staticmethod
    def _extract_row_page(cells: list[str]) -> tuple[int | None, str | None]:
        for index in range(len(cells) - 1, -1, -1):
            compact = re.sub(r"\s+", "", cells[index])
            match = _ROW_PAGE_CELL_PATTERN.fullmatch(compact)
            if match:
                return index, match.group("page")
        return None, None

    @staticmethod
    def _extract_exact_number(value: str) -> str | None:
        match = re.fullmatch(rf"({_BARE_NUMBERING_PATTERN_TEXT})", value.strip())
        if match is None:
            return None
        return match.group(1)

    @staticmethod
    def _split_number_and_title(value: str) -> tuple[str | None, str | None]:
        stripped = value.strip()
        match = re.match(
            rf"^(?P<number>{_NUMBERING_PATTERN_TEXT})\s+(?P<title>.+)$", stripped
        )
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
