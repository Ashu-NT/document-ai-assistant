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

        if len(parsed_rows) < max(3, len(self._non_empty_cells(rows)) // 2):
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
            row_entries: list[_ParsedTocEntry] = []
            for cell in row:
                row_entries.extend(self._parse_cell(cell))
            for entry in self._dedupe_row_entries(row_entries):
                parsed.append(entry)
        return parsed

    def _parse_cell(self, cell: str) -> list[_ParsedTocEntry]:
        entry = self._parse_entry(cell)
        if entry is None:
            return []
        return [entry]

    def _parse_entry(self, value: str) -> _ParsedTocEntry | None:
        text = repair_docling_text(str(value or "")).strip().strip("|").strip()
        if not text:
            return None

        text = re.sub(r"\s+", " ", text)
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

    def _looks_like_root_toc_title(self, value: str) -> bool:
        if any(character.isdigit() for character in value):
            return False

        alpha_tokens = self._ALPHA_TOKEN_PATTERN.findall(value)
        return 1 <= len(alpha_tokens) <= 6
