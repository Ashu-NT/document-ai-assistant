from __future__ import annotations

import re
from typing import Any

from src.application.langgraph.research.models import ResearchEvidence
from src.application.langgraph.research.presentation.table_text_summarizer import (
    TableTextSummarizer,
)


class EvidenceFindingExtractor:
    def __init__(
        self,
        *,
        table_summarizer: TableTextSummarizer | None = None,
    ) -> None:
        self.table_summarizer = table_summarizer or TableTextSummarizer()

    def extract(
        self,
        evidence: ResearchEvidence,
        *,
        task_title: str | None = None,
        max_findings: int = 4,
    ) -> list[dict[str, Any]]:
        text = self._strip_scaffolding(evidence.content_excerpt)
        if not text or self._is_noisy(text):
            return []

        topic_hint = self._topic_hint(evidence=evidence, task_title=task_title)
        table_pairs = self.table_summarizer.summarize(
            text,
            topic_hint=topic_hint,
            max_pairs=6,
        )
        if table_pairs:
            finding = self._table_finding(
                evidence=evidence,
                topic_hint=topic_hint,
                details=table_pairs,
            )
            return [finding] if finding is not None else []

        statements = self._extract_statements(text)
        findings: list[dict[str, Any]] = []
        for statement in statements:
            cleaned = self._clean_sentence(statement)
            if cleaned is None:
                continue
            findings.append(self._finding_payload(evidence=evidence, text=cleaned))
            if len(findings) >= max_findings:
                break
        return findings

    def _table_finding(
        self,
        *,
        evidence: ResearchEvidence,
        topic_hint: str,
        details: list[str],
    ) -> dict[str, Any] | None:
        if not details:
            return None
        intro = self._table_intro(
            topic_hint=topic_hint,
            chunk_type=evidence.chunk_type,
            section_path=evidence.section_path,
        )
        return self._finding_payload(
            evidence=evidence,
            text=intro,
            details=details,
        )

    def _table_intro(
        self,
        *,
        topic_hint: str,
        chunk_type: str | None,
        section_path: list[str],
    ) -> str:
        normalized_path = " ".join(section_path).casefold()
        normalized_type = (chunk_type or "").casefold()
        normalized_topic = topic_hint.casefold()
        if "maintenance" in normalized_topic or "interval" in normalized_topic:
            return "Maintenance-related structured evidence includes:"
        if "pump" in normalized_path:
            return "Pump technical data includes:"
        if "system" in normalized_path:
            return "System-level technical data includes:"
        if "press" in normalized_path:
            return "Food Waste Press technical data includes:"
        if "technical_specification" in normalized_type or "specification" in normalized_topic:
            return "Technical specifications include:"
        return "Structured document evidence includes:"

    @staticmethod
    def _finding_payload(
        *,
        evidence: ResearchEvidence,
        text: str,
        details: list[str] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "text": text,
            "document_title": evidence.document_title,
            "page_start": evidence.page_start,
            "page_end": evidence.page_end,
            "section_path": list(evidence.section_path),
            "chunk_type": evidence.chunk_type,
        }
        if details:
            payload["details"] = list(details)
        return payload

    def _extract_statements(self, text: str) -> list[str]:
        lines = self._normalized_lines(text)
        statements: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if self._is_heading_only(line):
                index += 1
                continue
            if line.endswith(":") and index + 1 < len(lines):
                statements.append(f"{line[:-1].strip()}: {lines[index + 1]}")
                index += 2
                continue
            statements.extend(re.split(r"(?<=[.!?])\s+", line))
            index += 1
        return statements

    @staticmethod
    def _strip_scaffolding(text: str) -> str:
        normalized = text or ""
        for prefix in ("Context:", "Section overview:", "Figure:", "OCR:"):
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :].strip()
        return normalized.strip()

    @staticmethod
    def _normalized_lines(text: str) -> list[str]:
        lines: list[str] = []
        for raw_line in text.splitlines():
            candidate = re.sub(r"^[\-\*\u2022\u25A0]+\s*", "", raw_line.strip())
            candidate = re.sub(r"^\d+\.\s*", "", candidate)
            candidate = re.sub(r"^(warning|warnings|caution|danger|note|notes)\s*:?\s*", "", candidate, flags=re.IGNORECASE)
            candidate = " ".join(candidate.split())
            if candidate:
                lines.append(candidate)
        return lines

    def _clean_sentence(self, value: str) -> str | None:
        candidate = value.strip(" -")
        if not candidate or self._is_heading_only(candidate):
            return None
        if candidate.endswith("...") or "..." in candidate:
            return None
        if len(candidate) < 10:
            return None
        if candidate.count("|") >= 2:
            return None
        if not re.search(r"[a-zA-Z]", candidate):
            return None
        return candidate if candidate.endswith((".", "!", "?")) else f"{candidate}."

    @staticmethod
    def _is_heading_only(value: str) -> bool:
        normalized = value.strip().lower().rstrip(":")
        return normalized in {"warning", "warnings", "caution", "danger", "note", "notes"}

    @staticmethod
    def _is_noisy(text: str) -> bool:
        normalized = text.casefold().strip()
        if not normalized:
            return True
        if normalized.startswith("table of contents"):
            return True
        if normalized.endswith("..."):
            return True
        return False

    @staticmethod
    def _topic_hint(*, evidence: ResearchEvidence, task_title: str | None) -> str:
        parts = [
            task_title or "",
            evidence.chunk_type or "",
            " ".join(evidence.section_path),
        ]
        return " ".join(part for part in parts if part).strip()
