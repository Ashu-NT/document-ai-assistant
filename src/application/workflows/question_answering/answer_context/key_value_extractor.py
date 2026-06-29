from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerKeyValue,
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
    AnswerSource,
)

_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    "Design Temperature": ("design temperature",),
    "Test pressure": ("test pressure",),
    "Design pressure": ("design pressure",),
    "Working pressure": ("working pressure",),
    "Pressure": ("pressure",),
    "Temperature": ("temperature",),
    "Size": ("size", "nominal size"),
    "Quantity": ("quantity", "qty"),
    "Material": ("material",),
    "Voltage": ("voltage",),
    "Current": ("current",),
    "Power": ("power",),
    "Capacity": ("capacity",),
    "Serial Number": ("serial number",),
    "Part Number": ("part number",),
    "Model": ("model", "model number"),
    "Order code": ("order code", "ordering code", "order number"),
    "DN": ("dn",),
    "Date of inspection": ("date of inspection", "inspection date"),
}
_TABLE_ROW_PATTERN = re.compile(r"^\|(?P<cells>.+)\|$")
_KEY_VALUE_PATTERN = re.compile(
    r"^(?P<key>[A-Za-z][A-Za-z0-9 /().%-]{1,80})\s*[:\-]\s*(?P<value>.+)$"
)
_INLINE_PATTERN = re.compile(
    r"\b(?P<key>"
    r"design temperature|test pressure|design pressure|working pressure|pressure|"
    r"temperature|size|quantity|material|voltage|current|power|capacity|dn|"
    r"serial number|part number|model(?: number)?|order(?:ing)? code|"
    r"date of inspection|inspection date"
    r")\b\s*(?:is|=)?\s*(?P<value>.+)$",
    re.IGNORECASE,
)
_UNIT_PATTERN = re.compile(r"\b(bar|mm|cm|m|kw|w|v|a|hz|dn|pcs|pc|c)\b", re.IGNORECASE)
_BULLET_PREFIX_PATTERN = re.compile(r"^\s*(?:[-*•]\s+|\d+[\).\s]+)")
_HEADER_SEPARATOR_PATTERN = re.compile(
    r"^\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?$"
)
_MAINTENANCE_INTERVAL_PATTERN = re.compile(
    r"\b("
    r"every\s+\d+\s+(?:operating\s+)?hours?"
    r"|every\s+\d+\s+(?:day|days|week|weeks|month|months|year|years)"
    r"|daily|weekly|monthly|quarterly|annually|yearly"
    r"|every\s+shift|before\s+each\s+\w+|after\s+each\s+\w+|at\s+each\s+\w+"
    r"|when\s+necessary|as\s+needed|if\s+necessary"
    r")\b",
    re.IGNORECASE,
)
_MAINTENANCE_ACTION_PATTERN = re.compile(
    r"\b("
    r"inspect|check|replace|lubricate|clean|test|drain|tighten|calibrate|"
    r"change|grease|service|flush|verify|examine|adjust|renew"
    r")\b",
    re.IGNORECASE,
)
_MAINTENANCE_LINE_HINTS = (
    "maintenance task",
    "maintenance tasks",
    "maintenance interval",
    "maintenance intervals",
    "maintenance schedule",
    "preventive maintenance",
    "service interval",
    "service schedule",
    "inspection schedule",
    "routine maintenance",
    "maintenance checklist",
)
_MAINTENANCE_COMPONENT_PATTERN = re.compile(
    r"^(?:inspect|check|replace|lubricate|clean|test|drain|tighten|calibrate|"
    r"change|grease|service|flush|verify|examine|adjust|renew)\s+"
    r"(?:(?:the|a|an)\s+)?(?P<component>[^,.;:]+)",
    re.IGNORECASE,
)
_TABLE_HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "task": (
        "task",
        "maintenance task",
        "maintenance item",
        "activity",
        "action",
        "operation",
    ),
    "interval": (
        "interval",
        "interval/frequency",
        "frequency",
        "frequency/interval",
        "period",
        "schedule",
    ),
    "component": ("component", "equipment", "part", "item", "location"),
    "notes": ("notes", "remark", "remarks", "comment", "comments", "details"),
}
_NOT_SPECIFIED = "Not specified"
_PLACEHOLDER_VALUES = {"x", "-", "n/a", "na", "unknown"}
_SUPPORTED_INTENTS = {
    AnswerIntent.SPECIFICATION_SUMMARY,
    AnswerIntent.CERTIFICATION_SUMMARY,
    AnswerIntent.TABLE_SUMMARY,
    AnswerIntent.IDENTIFIER_LOOKUP,
}


@dataclass(slots=True, frozen=True)
class _MaintenanceCandidate:
    task: str
    description: str | None
    interval: str
    component: str | None
    notes: str | None


class KeyValueExtractor:
    def extract(
        self,
        sources: Sequence[AnswerSource],
        *,
        answer_intent: AnswerIntent,
    ) -> list[AnswerKeyValue]:
        if answer_intent not in _SUPPORTED_INTENTS:
            return []

        key_values: list[AnswerKeyValue] = []
        seen: set[tuple[int, str, str]] = set()
        for source in sources:
            for raw_key, raw_value in self._candidate_pairs(source.content):
                key = self._normalize_key(raw_key)
                if key is None:
                    continue
                value = raw_value.strip().strip("|").strip()
                if not value:
                    continue
                fingerprint = (source.source_number, key.lower(), value.lower())
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                key_values.append(
                    AnswerKeyValue(
                        key=key,
                        value=value,
                        unit=self._extract_unit(value),
                        source_number=source.source_number,
                        confidence=0.9,
                    )
                )
        return key_values

    def extract_maintenance_entries(
        self,
        sources: Sequence[AnswerSource],
        *,
        answer_intent: AnswerIntent,
    ) -> list[AnswerMaintenanceEntry]:
        if answer_intent != AnswerIntent.MAINTENANCE_SUMMARY:
            return []

        entries: list[AnswerMaintenanceEntry] = []
        seen: set[tuple[int, str, str, str]] = set()
        for source in sources:
            for candidate in self._maintenance_candidates(source.content):
                fingerprint = (
                    source.source_number,
                    candidate.task.lower(),
                    candidate.interval.lower(),
                    (candidate.component or "").lower(),
                )
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                entries.append(
                    AnswerMaintenanceEntry(
                        task=candidate.task,
                        description=candidate.description,
                        interval=candidate.interval,
                        component=candidate.component,
                        notes=candidate.notes,
                        source_number=source.source_number,
                        source_numbers=[source.source_number],
                        page_start=source.page_start,
                        page_end=source.page_end,
                        section_path=source.section_path,
                        section_paths=[source.section_path] if source.section_path else [],
                        references=[
                            AnswerMaintenanceReference(
                                source_number=source.source_number,
                                page_start=source.page_start,
                                page_end=source.page_end,
                                section_path=source.section_path,
                            )
                        ],
                        confidence=0.88,
                    )
                )
        return entries

    def _candidate_pairs(self, content: str) -> list[tuple[str, str]]:
        pairs: list[tuple[str, str]] = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            table_match = _TABLE_ROW_PATTERN.match(stripped)
            if table_match is not None:
                cells = [cell.strip() for cell in table_match.group("cells").split("|")]
                if len(cells) >= 2 and cells[0] and cells[1]:
                    pairs.append((cells[0], cells[1]))
                continue

            key_value_match = _KEY_VALUE_PATTERN.match(stripped)
            if key_value_match is not None:
                pairs.append(
                    (
                        key_value_match.group("key"),
                        key_value_match.group("value"),
                    )
                )
                continue

            inline_match = _INLINE_PATTERN.search(stripped)
            if inline_match is not None:
                pairs.append((inline_match.group("key"), inline_match.group("value")))
        return pairs

    def _maintenance_candidates(
        self,
        content: str,
    ) -> list[_MaintenanceCandidate]:
        candidates: list[_MaintenanceCandidate] = []
        table_header: list[str] | None = None
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                table_header = None
                continue
            if _HEADER_SEPARATOR_PATTERN.match(stripped):
                continue
            if "|" in stripped:
                cells = self._table_cells(stripped)
                if len(cells) >= 2:
                    header = self._table_header(cells)
                    if header is not None:
                        table_header = header
                        continue
                    table_candidate = self._maintenance_candidate_from_table_row(
                        cells,
                        table_header=table_header,
                    )
                    if table_candidate is not None:
                        candidates.append(table_candidate)
                        continue

            line_candidate = self._maintenance_candidate_from_line(stripped)
            if line_candidate is not None:
                candidates.append(line_candidate)
        return candidates

    @staticmethod
    def _table_cells(line: str) -> list[str]:
        if line.startswith("|") and line.endswith("|"):
            line = line[1:-1]
        return [cell.strip() for cell in line.split("|")]

    def _table_header(self, cells: Sequence[str]) -> list[str] | None:
        normalized = [self._normalize_table_header(cell) for cell in cells]
        if any(value is None for value in normalized):
            return None
        if "task" not in normalized:
            return None
        return [value for value in normalized if value is not None]

    @staticmethod
    def _normalize_table_header(cell: str) -> str | None:
        normalized = " ".join(cell.lower().split())
        for canonical, aliases in _TABLE_HEADER_ALIASES.items():
            if normalized == canonical or normalized in aliases:
                return canonical
        return None

    def _maintenance_candidate_from_table_row(
        self,
        cells: Sequence[str],
        *,
        table_header: Sequence[str] | None,
    ) -> _MaintenanceCandidate | None:
        if not cells:
            return None
        if table_header is not None and len(table_header) == len(cells):
            mapped = {
                table_header[index]: cells[index].strip()
                for index in range(len(cells))
            }
            task = mapped.get("task", "").strip()
            if not task or not self._looks_like_maintenance_task(task):
                return None
            interval = self._clean_interval(mapped.get("interval"))
            component = self._clean_optional_text(mapped.get("component"))
            notes = self._clean_optional_text(mapped.get("notes"))
            if component is None:
                component = self._extract_component(task)
            return _MaintenanceCandidate(
                task=task,
                description=self._build_description(task, notes),
                interval=interval,
                component=component,
                notes=notes,
            )

        task_cell = next(
            (cell.strip() for cell in cells if self._looks_like_maintenance_task(cell)),
            None,
        )
        if task_cell is None:
            return None
        interval_cell = next(
            (cell.strip() for cell in cells if _MAINTENANCE_INTERVAL_PATTERN.search(cell)),
            None,
        )
        component = self._extract_component(task_cell)
        notes_candidates = [
            cell.strip()
            for cell in cells
            if cell.strip() and cell.strip() not in {task_cell, interval_cell}
        ]
        notes = self._clean_optional_text("; ".join(notes_candidates)) if notes_candidates else None
        return _MaintenanceCandidate(
            task=task_cell,
            description=self._build_description(task_cell, notes),
            interval=self._clean_interval(interval_cell),
            component=component,
            notes=notes,
        )

    def _maintenance_candidate_from_line(
        self,
        line: str,
    ) -> _MaintenanceCandidate | None:
        cleaned = _BULLET_PREFIX_PATTERN.sub("", line).strip()
        if not cleaned:
            return None
        lowered = cleaned.lower()
        if not self._looks_like_maintenance_line(lowered):
            return None

        interval_match = _MAINTENANCE_INTERVAL_PATTERN.search(cleaned)
        interval = self._clean_interval(interval_match.group(0) if interval_match else None)
        if interval_match is not None and interval_match.start() == 0:
            task_text = cleaned[interval_match.end() :].lstrip(" :-,")
            notes = None
        else:
            task_text, notes = self._split_task_and_notes(cleaned, interval_match)
        task = self._clean_task(task_text)
        if not task or not self._looks_like_maintenance_task(task):
            return None

        component = self._extract_component(task)
        notes = self._clean_optional_text(notes)
        return _MaintenanceCandidate(
            task=task,
            description=self._build_description(cleaned, notes, task=task),
            interval=interval,
            component=component,
            notes=notes,
        )

    @staticmethod
    def _looks_like_maintenance_line(line: str) -> bool:
        return bool(_MAINTENANCE_ACTION_PATTERN.search(line)) or any(
            marker in line for marker in _MAINTENANCE_LINE_HINTS
        ) or bool(_MAINTENANCE_INTERVAL_PATTERN.search(line))

    @staticmethod
    def _looks_like_maintenance_task(text: str) -> bool:
        cleaned = " ".join(text.strip().split())
        if not cleaned:
            return False
        lowered = cleaned.lower()
        if lowered in _MAINTENANCE_LINE_HINTS:
            return False
        return bool(_MAINTENANCE_ACTION_PATTERN.search(cleaned)) or bool(
            _MAINTENANCE_INTERVAL_PATTERN.search(cleaned)
        )

    def _split_task_and_notes(
        self,
        text: str,
        interval_match: re.Match[str] | None,
    ) -> tuple[str, str | None]:
        if interval_match is None:
            parts = re.split(r"(?<=[.;])\s+", text, maxsplit=1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
            return text, None

        task_text = text[: interval_match.start()].strip(" ,;:-")
        remainder = text[interval_match.end() :].strip(" ,;:-")
        if not task_text:
            task_text = text
            remainder = None
        return task_text, remainder or None

    @staticmethod
    def _clean_task(task: str | None) -> str | None:
        if task is None:
            return None
        cleaned = " ".join(task.strip().split())
        if ":" in cleaned:
            prefix, suffix = cleaned.split(":", 1)
            if _MAINTENANCE_ACTION_PATTERN.search(suffix):
                cleaned = suffix.strip()
        return cleaned.rstrip(" .;:") or None

    @staticmethod
    def _clean_interval(interval: str | None) -> str:
        cleaned = KeyValueExtractor._clean_optional_text(interval)
        if cleaned is None:
            return _NOT_SPECIFIED
        return cleaned or _NOT_SPECIFIED

    @staticmethod
    def _clean_optional_text(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        cleaned = cleaned.rstrip(" .;:")
        if not cleaned:
            return None
        if cleaned.lower() in _PLACEHOLDER_VALUES:
            return None
        return cleaned

    @staticmethod
    def _extract_component(task: str) -> str | None:
        match = _MAINTENANCE_COMPONENT_PATTERN.match(task)
        if match is None:
            return None
        component = " ".join(match.group("component").split())
        component = re.split(r"\b(?:for|during|before|after|when|if)\b", component, maxsplit=1)[0]
        return component.rstrip(" .;:") or None

    def _build_description(
        self,
        raw_line: str,
        notes: str | None,
        *,
        task: str | None = None,
    ) -> str | None:
        task_text = self._clean_optional_text(task or raw_line)
        notes_text = self._clean_optional_text(notes)
        if notes_text is not None and task_text is not None:
            return self._clean_optional_text(f"{task_text}. {notes_text}")
        return notes_text or task_text

    @staticmethod
    def _normalize_key(raw_key: str) -> str | None:
        normalized = " ".join(raw_key.lower().split())
        for canonical, aliases in _KEY_ALIASES.items():
            if normalized == canonical.lower():
                return canonical
            if normalized in aliases:
                return canonical
        return None

    @staticmethod
    def _extract_unit(value: str) -> str | None:
        match = _UNIT_PATTERN.search(value)
        if match is None:
            return None
        return match.group(1)
