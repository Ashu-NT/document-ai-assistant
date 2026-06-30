from __future__ import annotations

import re
from typing import Any

from src.application.langgraph.research.models import ResearchEvidence


class ResearchFindingBuilder:
    def build_findings(
        self,
        evidence: list[ResearchEvidence],
        *,
        max_findings: int = 5,
    ) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in evidence:
            for statement in self._extract_statements(item.content_excerpt):
                normalized = self._normalize_statement(statement)
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                findings.append(
                    {
                        "text": statement,
                        "document_title": item.document_title,
                        "page_start": item.page_start,
                        "page_end": item.page_end,
                        "section_path": list(item.section_path),
                        "chunk_type": item.chunk_type,
                    }
                )
                if len(findings) >= max_findings:
                    return findings
        return findings

    def _extract_statements(self, text: str) -> list[str]:
        cleaned = self._strip_scaffolding(text)
        table_statements = self._extract_table_statements(cleaned)
        if table_statements:
            return table_statements

        lines = self._normalized_lines(cleaned)
        statements: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if self._is_heading_only(line):
                index += 1
                continue
            if line.endswith(":") and index + 1 < len(lines):
                candidate = f"{line[:-1].strip()}: {lines[index + 1]}"
                statements.extend(self._split_sentences(candidate))
                index += 2
                continue
            statements.extend(self._split_sentences(line))
            index += 1
        return statements[:6]

    def _extract_table_statements(self, text: str) -> list[str]:
        rows = self._parse_table_rows(text)
        if len(rows) < 2:
            return []
        if len(rows) == 2 and len(rows[0]) == len(rows[1]) and len(rows[0]) > 1:
            return [
                self._ensure_period(f"{header}: {value}")
                for header, value in zip(rows[0], rows[1])
                if header and value
            ][:5]
        header = rows[0]
        if len(header) == 2 and len(rows) > 2:
            return [
                self._ensure_period(f"{row[0]}: {row[1]}")
                for row in rows[1:]
                if len(row) >= 2 and row[0] and row[1]
            ][:5]
        if len(header) > 2 and len(rows) > 2:
            first_data_row = rows[1]
            return [
                self._ensure_period(f"{header[index]}: {value}")
                for index, value in enumerate(first_data_row[: len(header)])
                if header[index] and value
            ][:5]
        return []

    @staticmethod
    def _strip_scaffolding(text: str) -> str:
        normalized = text or ""
        for prefix in ("Context:", "Section overview:", "Figure:", "OCR:"):
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :].strip()
        return normalized

    def _normalized_lines(self, text: str) -> list[str]:
        lines: list[str] = []
        for raw_line in text.splitlines():
            candidate = re.sub(r"^[\-\*\u2022\u25A0]+\s*", "", raw_line.strip())
            candidate = re.sub(r"^\d+\.\s*", "", candidate)
            candidate = " ".join(candidate.split())
            if candidate:
                lines.append(candidate)
        return lines

    def _split_sentences(self, value: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", value.strip())
        statements: list[str] = []
        for part in parts:
            candidate = self._clean_sentence(part)
            if candidate:
                statements.append(candidate)
        return statements

    def _clean_sentence(self, value: str) -> str | None:
        candidate = value.strip(" -")
        if not candidate:
            return None
        if self._is_heading_only(candidate):
            return None
        if len(candidate) < 10:
            return None
        return self._ensure_period(candidate)

    @staticmethod
    def _ensure_period(value: str) -> str:
        return value if value.endswith((".", "!", "?")) else f"{value}."

    @staticmethod
    def _normalize_statement(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()

    @staticmethod
    def _is_heading_only(value: str) -> bool:
        normalized = value.strip().lower().rstrip(":")
        return normalized in {"warning", "warnings", "caution", "danger", "note", "notes"}

    def _parse_table_rows(self, text: str) -> list[list[str]]:
        rows: list[list[str]] = []
        for line in text.splitlines():
            if "|" not in line:
                continue
            cells = [self._table_cell(cell) for cell in line.split("|")]
            cells = [cell for cell in cells if cell]
            if len(cells) < 2:
                continue
            if all(re.fullmatch(r"[:\-]+", cell) for cell in cells):
                continue
            rows.append(cells)
        return rows

    @staticmethod
    def _table_cell(value: str) -> str:
        return " ".join(value.strip().split())
