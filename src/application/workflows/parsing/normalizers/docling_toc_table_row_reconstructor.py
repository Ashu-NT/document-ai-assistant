from __future__ import annotations

import re

from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    extract_heading_number,
    strip_heading_number,
)
from src.application.workflows.parsing.normalizers.docling_text_cleaner import (
    repair_docling_text,
)


class DoclingTocTableRowReconstructor:
    _DOT_LEADER_PATTERN = re.compile(r"^(?P<title>.+?)\.{2,}\s*(?P<page>\d+)$")
    _SPACE_PAGE_PATTERN = re.compile(r"^(?P<title>.+?)\s+(?P<page>\d+)$")

    def reconstruct(self, rows: list[list[str]]) -> list[list[str]]:
        parsed_rows = self._parse_rows(rows)
        if len(parsed_rows) < 3:
            return rows

        if len(parsed_rows) < max(3, len(self._non_empty_cells(rows)) // 2):
            return rows

        include_numbering = any(numbering for numbering, _, _ in parsed_rows)
        header = (
            ["Number", "Title", "Page"]
            if include_numbering
            else ["Title", "Page"]
        )
        reconstructed = [header]
        for numbering, title, page in parsed_rows:
            if include_numbering:
                reconstructed.append([numbering, title, str(page)])
            else:
                reconstructed.append([title, str(page)])
        return reconstructed

    def _parse_rows(self, rows: list[list[str]]) -> list[tuple[str, str, int]]:
        parsed: list[tuple[str, str, int]] = []
        for row in rows:
            row_entries: list[tuple[str, str, int]] = []
            for cell in row:
                row_entries.extend(self._parse_cell(cell))
            for entry in self._dedupe_row_entries(row_entries):
                parsed.append(entry)
        return parsed

    def _parse_cell(self, cell: str) -> list[tuple[str, str, int]]:
        entry = self._parse_entry(cell)
        if entry is None:
            return []
        return [entry]

    def _parse_entry(self, value: str) -> tuple[str, str, int] | None:
        text = repair_docling_text(str(value or "")).strip().strip("|").strip()
        if not text:
            return None

        text = re.sub(r"\s+", " ", text)
        match = self._DOT_LEADER_PATTERN.match(text) or self._SPACE_PAGE_PATTERN.match(text)
        if match is None:
            return None

        title = match.group("title").strip()
        page = int(match.group("page"))
        numbering = extract_heading_number(title) or ""
        clean_title = strip_heading_number(title).strip(" .|-")
        if not clean_title:
            return None
        return numbering, clean_title, page

    @staticmethod
    def _dedupe_row_entries(
        entries: list[tuple[str, str, int]],
    ) -> list[tuple[str, str, int]]:
        deduped: list[tuple[str, str, int]] = []
        seen: set[tuple[str, str, int]] = set()
        for entry in entries:
            if entry in seen:
                continue
            seen.add(entry)
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
