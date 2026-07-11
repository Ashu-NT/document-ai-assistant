from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from src.application.workflows.question_answering.answer_context.maintenance.maintenance_task_text_cleaner import (
    clean_task,
)
from src.application.workflows.shared.maintenance_action_verbs import (
    MAINTENANCE_ACTION_VERBS,
)
from src.application.workflows.shared.maintenance_text_cleaning import (
    clean_interval,
    clean_optional_text,
)

_BULLET_PREFIX_PATTERN = re.compile(r"^\s*(?:[-*•]\s+|\d+[\).\s]+)")
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
    r"\b(" + "|".join(MAINTENANCE_ACTION_VERBS) + r")\b",
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
    r"^(?:" + "|".join(MAINTENANCE_ACTION_VERBS) + r")\s+"
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


@dataclass(slots=True, frozen=True)
class MaintenanceCandidate:
    task: str
    description: str | None
    interval: str
    component: str | None
    notes: str | None


def parse_table_cells(line: str) -> list[str]:
    if line.startswith("|") and line.endswith("|"):
        line = line[1:-1]
    return [cell.strip() for cell in line.split("|")]


def parse_table_header(cells: Sequence[str]) -> list[str] | None:
    normalized = [_normalize_table_header_cell(cell) for cell in cells]
    if any(value is None for value in normalized):
        return None
    if "task" not in normalized:
        return None
    return [value for value in normalized if value is not None]


def _normalize_table_header_cell(cell: str) -> str | None:
    normalized = " ".join(cell.lower().split())
    for canonical, aliases in _TABLE_HEADER_ALIASES.items():
        if normalized == canonical or normalized in aliases:
            return canonical
    return None


def candidate_from_table_row(
    cells: Sequence[str],
    *,
    table_header: Sequence[str] | None,
) -> MaintenanceCandidate | None:
    if not cells:
        return None
    if table_header is not None and len(table_header) == len(cells):
        mapped = {
            table_header[index]: cells[index].strip()
            for index in range(len(cells))
        }
        task = mapped.get("task", "").strip()
        if not task or not looks_like_maintenance_task(task):
            return None
        interval = clean_interval(mapped.get("interval"))
        component = clean_optional_text(mapped.get("component"))
        notes = clean_optional_text(mapped.get("notes"))
        if component is None:
            component = extract_component(task)
        return MaintenanceCandidate(
            task=task,
            description=build_description(task, notes),
            interval=interval,
            component=component,
            notes=notes,
        )

    task_cell = next(
        (cell.strip() for cell in cells if looks_like_maintenance_task(cell)),
        None,
    )
    if task_cell is None:
        return None
    interval_cell = next(
        (cell.strip() for cell in cells if _MAINTENANCE_INTERVAL_PATTERN.search(cell)),
        None,
    )
    component = extract_component(task_cell)
    notes_candidates = [
        cell.strip()
        for cell in cells
        if cell.strip() and cell.strip() not in {task_cell, interval_cell}
    ]
    notes = clean_optional_text("; ".join(notes_candidates)) if notes_candidates else None
    return MaintenanceCandidate(
        task=task_cell,
        description=build_description(task_cell, notes),
        interval=clean_interval(interval_cell),
        component=component,
        notes=notes,
    )


def candidate_from_line(line: str) -> MaintenanceCandidate | None:
    cleaned = _BULLET_PREFIX_PATTERN.sub("", line).strip()
    if not cleaned:
        return None
    lowered = cleaned.lower()
    if not looks_like_maintenance_line(lowered):
        return None

    interval_match = _MAINTENANCE_INTERVAL_PATTERN.search(cleaned)
    interval = clean_interval(interval_match.group(0) if interval_match else None)
    if interval_match is not None and interval_match.start() == 0:
        task_text = cleaned[interval_match.end() :].lstrip(" :-,")
        notes = None
    else:
        task_text, notes = split_task_and_notes(cleaned, interval_match)
    task = clean_task(task_text)
    if not task or not looks_like_maintenance_task(task):
        return None

    component = extract_component(task)
    notes = clean_optional_text(notes)
    return MaintenanceCandidate(
        task=task,
        description=build_description(cleaned, notes, task=task),
        interval=interval,
        component=component,
        notes=notes,
    )


def looks_like_maintenance_line(line: str) -> bool:
    return bool(_MAINTENANCE_ACTION_PATTERN.search(line)) or any(
        marker in line for marker in _MAINTENANCE_LINE_HINTS
    ) or bool(_MAINTENANCE_INTERVAL_PATTERN.search(line))


def looks_like_maintenance_task(text: str) -> bool:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return False
    lowered = cleaned.lower()
    if lowered in _MAINTENANCE_LINE_HINTS:
        return False
    return bool(_MAINTENANCE_ACTION_PATTERN.search(cleaned)) or bool(
        _MAINTENANCE_INTERVAL_PATTERN.search(cleaned)
    )


def split_task_and_notes(
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


def extract_component(task: str) -> str | None:
    match = _MAINTENANCE_COMPONENT_PATTERN.match(task)
    if match is None:
        return None
    component = " ".join(match.group("component").split())
    component = re.split(r"\b(?:for|during|before|after|when|if)\b", component, maxsplit=1)[0]
    return component.rstrip(" .;:") or None


def build_description(
    raw_line: str,
    notes: str | None,
    *,
    task: str | None = None,
) -> str | None:
    task_text = clean_optional_text(task or raw_line)
    notes_text = clean_optional_text(notes)
    if notes_text is not None and task_text is not None:
        return clean_optional_text(f"{task_text}. {notes_text}")
    return notes_text or task_text
