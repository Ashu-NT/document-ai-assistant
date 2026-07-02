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
    "Only partial row content was available in the retrieved context."
)
_EXPORT_FORMAT_MARKERS = ("markdown", "csv", "export", "spreadsheet", ".csv", ".md")
_SPARE_PARTS_REQUEST_MARKERS = ("spare part", "spare parts")
_MAX_RAW_ROWS_PER_GROUP = 25

_HEADER_SEPARATOR_PATTERN = re.compile(
    r"^\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?$"
)

# Only an exact match against one of these aliases counts as a header cell.
# Real-world exports frequently squeeze several column labels into a single
# cell (e.g. "Qty: Denomination: Spare Part No:") -- a fuzzy/startswith match
# would misread that merged cell as a single clean column and corrupt every
# row parsed underneath it, so we deliberately do not do fuzzy matching here.
_ROW_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "position": (
        "position no",
        "position no.",
        "position",
        "pos nr",
        "pos nr.",
        "pos no",
        "item",
        "item no",
    ),
    "pid_position": (
        "p&id pos nr",
        "p&id pos nr.",
        "p&id position",
        "p&id",
    ),
    "quantity": ("qty", "quantity"),
    "denomination": ("denomination",),
    "description": ("description",),
    "type": ("type",),
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
    "service": ("service", "function"),
}
_CONTENT_FIELDS = (
    "denomination",
    "description",
    "type",
    "part_no",
    "pid_position",
    "service",
)
_ROW_FIELD_LABELS: dict[str, str] = {
    "position": "Position",
    "pid_position": "P&ID Position",
    "quantity": "Quantity",
    "service": "Service",
    "type": "Type",
    "denomination": "Denomination",
    "description": "Description",
    "part_no": "Spare Part No.",
    "service_package": "Service package",
}
_ROW_FIELD_ORDER = (
    "position",
    "pid_position",
    "quantity",
    "service",
    "type",
    "denomination",
    "description",
    "part_no",
    "service_package",
)
_UNIT_ONLY_VALUES = {"pce", "pcs", "pc", "ea", "each", "unit", "units", "no", "no."}

_TABLE_EVIDENCE_PHRASE = "spare parts list"
_TABLE_HEADER_EVIDENCE_MARKERS = (
    "position no",
    "qty",
    "denomination",
    "spare part no",
    "part no",
    "p&id",
    "included in service package",
    "exploded views",
)
_BOILERPLATE_MARKERS = (
    "take note",
    "use of original manufacturer",
    "exempt",
    "nullify liability",
    "authorised by",
)
_PID_ROW_PATTERN = re.compile(
    r"^(?P<pid>[A-Za-z]{1,4}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(?P<rest>.+)$"
)
_TRAILING_PART_NO_PATTERN = re.compile(
    r"(?P<part_no>[A-Za-z]{0,3}\d{2,6}(?:[./]\d{1,3})?)\s*$"
)


@dataclass(slots=True, frozen=True)
class _SparePartsGroup:
    section_title: str
    section_path: str | None
    page_start: int | None
    page_end: int | None
    rows: list[dict[str, str]]
    raw_rows: list[str]
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

        groups: list[_SparePartsGroup] = []
        for chunk in chunks:
            if chunk.chunk_type != ChunkType.SPARE_PARTS_TABLE:
                continue
            if not self._has_table_evidence(chunk):
                continue
            groups.append(self._build_group(chunk))
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

    def _has_table_evidence(self, chunk: RetrievedChunk) -> bool:
        section_title = self._section_title(chunk).lower()
        if _TABLE_EVIDENCE_PHRASE in section_title:
            return True
        content_lower = chunk.content.lower()
        if _TABLE_EVIDENCE_PHRASE in content_lower:
            return True
        return any(marker in content_lower for marker in _TABLE_HEADER_EVIDENCE_MARKERS)

    @staticmethod
    def _section_title(chunk: RetrievedChunk) -> str:
        return (
            (chunk.citation.section_title if chunk.citation is not None else None)
            or (chunk.section_path[-1] if chunk.section_path else None)
            or "Spare Parts List"
        )

    def _build_group(self, chunk: RetrievedChunk) -> _SparePartsGroup:
        section_path = chunk.section_path_text() if chunk.section_path else None
        rows, raw_rows, partial = self._extract_rows(chunk.content)
        return _SparePartsGroup(
            section_title=self._section_title(chunk),
            section_path=section_path,
            page_start=chunk.source.page_start,
            page_end=chunk.source.page_end,
            rows=rows,
            raw_rows=raw_rows[:_MAX_RAW_ROWS_PER_GROUP],
            partial=partial or len(raw_rows) > _MAX_RAW_ROWS_PER_GROUP,
        )

    def _extract_rows(
        self,
        content: str,
    ) -> tuple[list[dict[str, str]], list[str], bool]:
        header: list[str | None] | None = None
        rows: list[dict[str, str]] = []
        raw_rows: list[str] = []
        dropped_row_count = 0
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or "|" not in line:
                continue
            if _HEADER_SEPARATOR_PATTERN.match(line):
                continue
            cells = self._split_cells(line)
            if header is None:
                header_candidate = self._as_header(cells)
                if header_candidate is not None:
                    header = header_candidate
                    continue

            if header is not None and len(cells) >= 2:
                row = self._row_from_cells(cells, header)
                if row is not None:
                    rows.append(row)
                else:
                    dropped_row_count += 1
                continue

            # No reliable header established for this chunk yet -- fall back
            # to inspecting each cell independently instead of inventing a
            # column layout that does not actually exist in the source.
            for cell in cells:
                self._handle_free_form_cell(cell, rows, raw_rows)

        partial = header is None or dropped_row_count > 0 or bool(raw_rows) or not rows
        return rows, raw_rows, partial

    def _handle_free_form_cell(
        self,
        cell: str,
        rows: list[dict[str, str]],
        raw_rows: list[str],
    ) -> None:
        text = cell.strip()
        if not text:
            return
        pid_match = _PID_ROW_PATTERN.match(text)
        if pid_match is not None:
            row = self._row_from_pid_match(pid_match)
            if row is not None:
                rows.append(row)
                return
        if self._looks_like_content_fragment(text):
            raw_rows.append(text)

    def _row_from_pid_match(self, match: re.Match[str]) -> dict[str, str] | None:
        pid = match.group("pid")
        rest = match.group("rest").strip()
        row: dict[str, str] = {"pid_position": pid}
        part_no_match = _TRAILING_PART_NO_PATTERN.search(rest)
        description = rest
        if part_no_match is not None:
            candidate = part_no_match.group("part_no")
            if candidate and candidate.lower() != pid.lower():
                description = rest[: part_no_match.start()].strip(" ,;:-")
                row["part_no"] = candidate
        if description:
            row["description"] = description
        if not self._has_identifying_content(row):
            return None
        return row

    @staticmethod
    def _looks_like_content_fragment(text: str) -> bool:
        if len(text) > 240:
            return False
        lowered = text.lower()
        if lowered.strip() == _TABLE_EVIDENCE_PHRASE:
            return False
        if any(marker in lowered for marker in _BOILERPLATE_MARKERS):
            return False
        return bool(re.search(r"\d", text))

    @staticmethod
    def _split_cells(line: str) -> list[str]:
        stripped = line
        if stripped.startswith("|"):
            stripped = stripped[1:]
        if stripped.endswith("|"):
            stripped = stripped[:-1]
        return [cell.strip() for cell in stripped.split("|")]

    @staticmethod
    def _normalize_cell(cell: str) -> str:
        return " ".join(cell.lower().strip(" :").split())

    @classmethod
    def _as_header(cls, cells: Sequence[str]) -> list[str | None] | None:
        normalized_cells = [cls._normalize_cell(cell) for cell in cells]
        mapped: list[str | None] = []
        seen_fields: set[str] = set()
        content_field_found = False
        for cell in normalized_cells:
            field_key = cls._exact_field_for_cell(cell)
            if field_key is not None:
                if field_key in seen_fields:
                    return None
                seen_fields.add(field_key)
                if field_key in _CONTENT_FIELDS:
                    content_field_found = True
            mapped.append(field_key)
        if len(seen_fields) < 2 or not content_field_found:
            return None
        return mapped

    @staticmethod
    def _exact_field_for_cell(cell: str) -> str | None:
        for key, aliases in _ROW_FIELD_ALIASES.items():
            if cell in aliases:
                return key
        return None

    @classmethod
    def _row_from_cells(
        cls,
        cells: Sequence[str],
        header: Sequence[str | None],
    ) -> dict[str, str] | None:
        row: dict[str, str] = {}
        for index, field_key in enumerate(header):
            if field_key is None or index >= len(cells):
                continue
            value = cells[index].strip().strip(":").strip()
            if not value or value in {"-", "|"}:
                continue
            row[field_key] = value
        if not row:
            return None
        if not cls._has_identifying_content(row):
            return None
        return row

    @staticmethod
    def _has_identifying_content(row: dict[str, str]) -> bool:
        for field_key in _CONTENT_FIELDS:
            value = row.get(field_key)
            if value and value.strip().lower() not in _UNIT_ONLY_VALUES:
                return True
        return False

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
            if group.rows or group.raw_rows:
                lines.append("   Available rows:")
                for row in group.rows:
                    self._append_row_lines(lines, row)
                for raw_row in group.raw_rows:
                    lines.append(f"   - Raw row: {raw_row}")
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
