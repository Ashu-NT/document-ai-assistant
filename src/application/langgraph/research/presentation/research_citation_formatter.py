from __future__ import annotations

import re
from collections import OrderedDict
from typing import Any


class ResearchCitationFormatter:
    _PREFERRED_SECTION_TERMS = (
        "technical data",
        "specification",
        "preventive maintenance",
        "maintenance intervals",
        "oil quantities",
        "screen basket",
        "safety precautions",
        "troubleshooting",
        "technical specification",
        "lubrication",
    )
    _NOISY_SECTION_TERMS = (
        "components",
        "overview",
        "overview & maintenance intervals",
        "maintenance",
        "shutdown",
        "modifications",
        "spare parts",
        "chapter",
        "section",
    )

    def display_document_name(self, value: str | None) -> str:
        if isinstance(value, str):
            normalized = value.strip()
            if normalized and not re.fullmatch(
                r"doc[_-][a-f0-9]{8,}",
                normalized,
                re.IGNORECASE,
            ):
                return normalized
        return "Selected Document"

    def simplify_section_path(self, section_path: list[str] | None) -> str | None:
        if not isinstance(section_path, list):
            return None
        cleaned = self._cleaned_path(section_path)
        if not cleaned:
            return None
        if len(cleaned) <= 2:
            return " -> ".join(cleaned)

        tail_index = self._best_tail_index(cleaned)
        parent_index = self._best_parent_index(cleaned, tail_index)
        if parent_index is None:
            return cleaned[tail_index]
        selected = [cleaned[parent_index], cleaned[tail_index]]
        return " -> ".join(selected)

    def format_inline_citation(self, reference: dict[str, Any]) -> str:
        document_name = self.display_document_name(
            self._str_or_none(reference.get("document_title"))
            or self._str_or_none(reference.get("document_name"))
        )
        page_label = self.format_page_label(
            reference.get("page_start"),
            reference.get("page_end"),
        )
        if page_label:
            return f"({document_name}, {page_label})"
        return f"({document_name})"

    def format_reference_detail(self, reference: dict[str, Any]) -> str | None:
        document_name = self.display_document_name(
            self._str_or_none(reference.get("document_title"))
            or self._str_or_none(reference.get("document_name"))
        )
        page_label = self.format_page_label(
            reference.get("page_start"),
            reference.get("page_end"),
        )
        return f"{document_name}, {page_label}" if page_label else document_name

    def format_path_detail(self, reference: dict[str, Any]) -> str | None:
        return self.simplify_section_path(reference.get("section_path"))

    def format_page_label(self, page_start: Any, page_end: Any) -> str | None:
        start = self._to_int(page_start)
        end = self._to_int(page_end)
        if start is None:
            return None
        if end is None or end == start:
            return f"p.{start}"
        return f"pp.{start}\u2013{end}"

    def format_page_list(self, spans: list[tuple[int, int]]) -> str | None:
        if not spans:
            return None
        ordered = self._merge_page_spans(
            sorted(set(spans), key=lambda item: (item[0], item[1]))
        )
        labels = [
            str(start) if start == end else f"{start}\u2013{end}"
            for start, end in ordered
        ]
        prefix = "p." if len(labels) == 1 and ordered[0][0] == ordered[0][1] else "pp."
        return f"{prefix}{', '.join(labels)}"

    def build_reference_entries(
        self,
        references: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: "OrderedDict[tuple[str, str | None], dict[str, Any]]" = OrderedDict()
        for reference in references:
            if not isinstance(reference, dict):
                continue
            document_name = self.display_document_name(
                self._str_or_none(reference.get("document_title"))
                or self._str_or_none(reference.get("document_name"))
            )
            simplified_path = self.simplify_section_path(reference.get("section_path"))
            key = (document_name, simplified_path)
            entry = grouped.setdefault(
                key,
                {
                    "document_name": document_name,
                    "page_spans": [],
                    "section_path": simplified_path,
                },
            )
            span = self._page_span(reference)
            if span is not None:
                entry["page_spans"].append(span)
        return list(grouped.values())

    def _cleaned_path(self, section_path: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in section_path:
            if not isinstance(item, str):
                continue
            label = self._clean_section_label(item)
            if not label:
                continue
            normalized = label.casefold()
            if normalized in seen:
                continue
            seen.add(normalized)
            cleaned.append(label)
        return cleaned

    def _best_tail_index(self, cleaned: list[str]) -> int:
        scored = [
            (
                self._section_score(label, prefer_terminal=True),
                index,
            )
            for index, label in enumerate(cleaned)
        ]
        return max(scored, key=lambda item: (item[0], item[1]))[1]

    def _best_parent_index(self, cleaned: list[str], tail_index: int) -> int | None:
        candidates = [
            (
                self._section_score(label, prefer_terminal=False),
                index,
            )
            for index, label in enumerate(cleaned[:tail_index])
        ]
        if not candidates:
            return None
        best_score, best_index = max(candidates, key=lambda item: (item[0], item[1]))
        if best_score <= 0:
            return max(0, tail_index - 1)
        return best_index

    def _section_score(self, label: str, *, prefer_terminal: bool) -> int:
        normalized = label.casefold()
        score = 0
        for rank, term in enumerate(self._PREFERRED_SECTION_TERMS):
            if term in normalized:
                score += 30 - rank
        for term in self._NOISY_SECTION_TERMS:
            if term in normalized:
                score -= 12
        if re.search(r"\b(press|pump|system|basket|motor|certificate|report|drawing)\b", normalized):
            score += 12
        if prefer_terminal:
            if re.search(r"\b(maintenance|specification|technical|procedure|troubleshooting|safety)\b", normalized):
                score += 10
        elif re.search(r"\b(press|pump|system|basket|manual|report|drawing)\b", normalized):
            score += 10
        return score

    def _page_span(self, reference: dict[str, Any]) -> tuple[int, int] | None:
        start = self._to_int(reference.get("page_start"))
        end = self._to_int(reference.get("page_end"))
        if start is None:
            return None
        return (start, end if end is not None else start)

    @staticmethod
    def _merge_page_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not spans:
            return []
        merged: list[tuple[int, int]] = [spans[0]]
        for start, end in spans[1:]:
            current_start, current_end = merged[-1]
            if start <= current_end + 1:
                merged[-1] = (current_start, max(current_end, end))
                continue
            merged.append((start, end))
        return merged

    @staticmethod
    def _clean_section_label(value: str) -> str:
        without_prefix = re.sub(r"^\s*\d+(?:\.\d+)*\s*", "", value.strip())
        normalized = " ".join(without_prefix.split())
        return normalized.strip(" >-")

    @staticmethod
    def _str_or_none(value: Any) -> str | None:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    @staticmethod
    def _to_int(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None
