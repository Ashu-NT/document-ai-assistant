from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.domain.common import ChunkType
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

_SUPPORTED_INTENTS = {AnswerIntent.TABLE_SUMMARY, AnswerIntent.IDENTIFIER_LOOKUP}
_PARTIAL_CONTENT_NOTICE = (
    "Only partial table content was available in the retrieved context."
)
_HEADER_SEPARATOR_PATTERN = re.compile(
    r"^\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?$"
)
_ROW_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "position": (
        "position no",
        "position no.",
        "position",
        "p&id pos nr",
        "p&id pos nr.",
        "pos nr",
        "pos no",
        "item",
        "item no",
    ),
    "quantity": ("qty", "qty:", "quantity"),
    "denomination": ("denomination", "description"),
    "part_no": (
        "spare part no",
        "spare part no.",
        "part no",
        "part no.",
        "part number",
    ),
    "service_package": (
        "included in service package",
        "service package",
    ),
}
_ROW_FIELD_LABELS: dict[str, str] = {
    "position": "Position",
    "quantity": "Quantity",
    "denomination": "Denomination",
    "part_no": "Spare Part No.",
    "service_package": "Service package",
}
_ROW_FIELD_ORDER = ("position", "quantity", "denomination", "part_no", "service_package")
_EXPORT_FORMAT_MARKERS = ("markdown", "csv", "export", "spreadsheet", ".csv", ".md")
_SPARE_PARTS_REQUEST_MARKERS = ("spare part", "spare parts")


@dataclass(slots=True, frozen=True)
class _SparePartsGroup:
    section_title: str
    section_path: str | None
    page_start: int | None
    page_end: int | None
    rows: list[dict[str, str]]
    partial: bool


class SparePartsListRenderer:
    def render(
        self,
        *,
        question: str,
        answer_intent: AnswerIntent | None,
        chunks: Sequence[RetrievedChunk],
    ) -> str | None:
        if answer_intent not in _SUPPORTED_INTENTS:
            return None
        if not self._looks_like_spare_parts_request(question):
            return None
        if self._wants_export_format(question):
            return None

        spare_parts_chunks = [
            chunk for chunk in chunks if chunk.chunk_type == ChunkType.SPARE_PARTS_TABLE
        ]
        if not spare_parts_chunks:
            return None

        groups = [self._build_group(chunk) for chunk in spare_parts_chunks]
        if not groups:
            return None

        return self._render_groups(groups)

    @staticmethod
    def _looks_like_spare_parts_request(question: str) -> bool:
        normalized = " ".join((question or "").strip().lower().split())
        return any(marker in normalized for marker in _SPARE_PARTS_REQUEST_MARKERS)

    @staticmethod
    def _wants_export_format(question: str) -> bool:
        normalized = (question or "").strip().lower()
        return any(marker in normalized for marker in _EXPORT_FORMAT_MARKERS)

    def _build_group(self, chunk: RetrievedChunk) -> _SparePartsGroup:
        section_path = chunk.section_path_text() if chunk.section_path else None
        section_title = (
            (chunk.citation.section_title if chunk.citation is not None else None)
            or (chunk.section_path[-1] if chunk.section_path else None)
            or "Spare Parts List"
        )
        rows, partial = self._extract_rows(chunk.content)
        return _SparePartsGroup(
            section_title=section_title,
            section_path=section_path,
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
            rows=rows,
            partial=partial,
        )

    def _extract_rows(self, content: str) -> tuple[list[dict[str, str]], bool]:
        header: list[str | None] | None = None
        rows: list[dict[str, str]] = []
        unresolved_row_count = 0
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or "|" not in line:
                continue
            if _HEADER_SEPARATOR_PATTERN.match(line):
                continue
            cells = self._split_cells(line)
            if len(cells) < 2:
                continue
            header_candidate = self._as_header(cells)
            if header_candidate is not None:
                header = header_candidate
                continue
            if header is None:
                unresolved_row_count += 1
                continue
            row = self._row_from_cells(cells, header)
            if row:
                rows.append(row)
        partial = header is None or unresolved_row_count > 0 or not rows
        return rows, partial

    @staticmethod
    def _split_cells(line: str) -> list[str]:
        stripped = line
        if stripped.startswith("|"):
            stripped = stripped[1:]
        if stripped.endswith("|"):
            stripped = stripped[:-1]
        return [cell.strip() for cell in stripped.split("|")]

    @staticmethod
    def _as_header(cells: Sequence[str]) -> list[str | None] | None:
        normalized_cells = [
            " ".join(cell.lower().strip(" :").split()) for cell in cells
        ]
        mapped: list[str | None] = []
        matches = 0
        for cell in normalized_cells:
            field = None
            for key, aliases in _ROW_FIELD_ALIASES.items():
                if cell in aliases or any(cell.startswith(alias) for alias in aliases):
                    field = key
                    matches += 1
                    break
            mapped.append(field)
        if matches < 2:
            return None
        return mapped

    @staticmethod
    def _row_from_cells(
        cells: Sequence[str],
        header: Sequence[str | None],
    ) -> dict[str, str]:
        row: dict[str, str] = {}
        for index, field in enumerate(header):
            if field is None or index >= len(cells):
                continue
            value = cells[index].strip().strip(":").strip()
            if not value or value in {"-", "|"}:
                continue
            row[field] = value
        return row

    def _render_groups(self, groups: Sequence[_SparePartsGroup]) -> str:
        lines = ["Spare parts lists found:", ""]
        for index, group in enumerate(groups, start=1):
            lines.append(f"{index}. {group.section_title}")
            lines.append(
                f"   Pages: {self._page_range(group.page_start, group.page_end)}"
            )
            lines.append(f"   Section: {group.section_path or '-'}")
            lines.append("   Type: spare_parts_table")
            lines.append("")
            if group.rows:
                lines.append("   Available rows:")
                for row in group.rows:
                    self._append_row_lines(lines, row)
            if group.partial:
                lines.append(f"   {_PARTIAL_CONTENT_NOTICE}")
            if index < len(groups):
                lines.append("")
        return "\n".join(lines).strip()

    @staticmethod
    def _append_row_lines(lines: list[str], row: dict[str, str]) -> None:
        first = True
        for field in _ROW_FIELD_ORDER:
            if field not in row:
                continue
            prefix = "   - " if first else "     "
            lines.append(f"{prefix}{_ROW_FIELD_LABELS[field]}: {row[field]}")
            first = False

    @staticmethod
    def _page_range(page_start: int | None, page_end: int | None) -> str:
        if page_start is None and page_end is None:
            return "-"
        if page_end is None or page_end == page_start:
            return str(page_start)
        return f"{page_start}-{page_end}"
