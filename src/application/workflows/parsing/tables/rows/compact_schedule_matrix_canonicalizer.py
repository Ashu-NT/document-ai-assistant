from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    SCHEDULE_INTERVAL_LABELS,
    looks_boolean_marker,
    normalize_cell,
)

_NOTE_HEADER_MARKERS = ("comment", "note", "notes", "reference", "remark")
_TASK_HEADER_MARKERS = ("activity", "action", "description", "task")
_NOTE_VALUE_MARKERS = (
    "annex",
    "manual",
    "note",
    "page",
    "reference",
    "refer to",
    "see ",
)


@dataclass(frozen=True)
class _OriginalColumnPlan:
    expanded_indexes: tuple[int, ...]
    kind: str


@dataclass(frozen=True)
class _HeaderPlan:
    expanded_headers: tuple[str, ...]
    columns: tuple[_OriginalColumnPlan, ...]
    task_index: int | None
    notes_index: int | None


class CompactScheduleMatrixCanonicalizer:
    def canonicalize(self, rows: list[list[str]]) -> list[list[str]] | None:
        if len(rows) < 2:
            return None
        plan = self._build_header_plan(rows[0])
        if plan is None:
            return None

        normalized_rows = [list(plan.expanded_headers)]
        for row in rows[1:]:
            normalized_rows.append(self._normalize_row(row, plan))
        return normalized_rows

    def _build_header_plan(self, header_row: list[str]) -> _HeaderPlan | None:
        expanded_headers: list[str] = []
        columns: list[_OriginalColumnPlan] = []
        schedule_label_count = 0
        task_index: int | None = None
        notes_index: int | None = None
        generic_indexes: list[int] = []

        for raw_header in header_row:
            header = normalize_cell(raw_header)
            schedule_labels = self._schedule_labels(header)
            if schedule_labels:
                start = len(expanded_headers)
                expanded_headers.extend(schedule_labels)
                columns.append(
                    _OriginalColumnPlan(
                        expanded_indexes=tuple(
                            range(start, start + len(schedule_labels))
                        ),
                        kind="schedule",
                    )
                )
                schedule_label_count += len(schedule_labels)
                continue

            normalized = header.casefold()
            contains_task = any(marker in normalized for marker in _TASK_HEADER_MARKERS)
            contains_note = any(marker in normalized for marker in _NOTE_HEADER_MARKERS)
            if contains_task and contains_note:
                task_index = len(expanded_headers)
                notes_index = len(expanded_headers) + 1
                expanded_headers.extend(["Task", "Notes"])
                columns.append(
                    _OriginalColumnPlan(
                        expanded_indexes=(task_index, notes_index),
                        kind="task_notes",
                    )
                )
                continue
            if contains_task:
                task_index = len(expanded_headers)
                expanded_headers.append("Task")
                columns.append(
                    _OriginalColumnPlan(
                        expanded_indexes=(task_index,),
                        kind="task",
                    )
                )
                continue
            if contains_note:
                notes_index = len(expanded_headers)
                expanded_headers.append("Notes")
                columns.append(
                    _OriginalColumnPlan(
                        expanded_indexes=(notes_index,),
                        kind="notes",
                    )
                )
                continue

            generic_index = len(expanded_headers)
            expanded_headers.append(header or f"Column {generic_index + 1}")
            generic_indexes.append(generic_index)
            columns.append(
                _OriginalColumnPlan(
                    expanded_indexes=(generic_index,),
                    kind="generic",
                )
            )

        if schedule_label_count < 2:
            return None
        if task_index is None:
            if generic_indexes:
                task_index = generic_indexes[-1]
                expanded_headers[task_index] = "Task"
            else:
                task_index = len(expanded_headers)
                expanded_headers.append("Task")
        return _HeaderPlan(
            expanded_headers=tuple(expanded_headers),
            columns=tuple(columns),
            task_index=task_index,
            notes_index=notes_index,
        )

    def _normalize_row(self, row: list[str], plan: _HeaderPlan) -> list[str]:
        normalized = [""] * len(plan.expanded_headers)
        pending_tasks: list[str] = []
        pending_notes: list[str] = []

        for column_index, column in enumerate(plan.columns):
            cell = normalize_cell(row[column_index]) if column_index < len(row) else ""
            if not cell:
                continue

            if column.kind == "schedule":
                distributed = self._distribute_schedule_cell(
                    cell,
                    target_count=len(column.expanded_indexes),
                )
                if distributed is None:
                    if self._looks_note_like(cell):
                        pending_notes.append(cell)
                    else:
                        pending_tasks.append(cell)
                    continue
                for target_index, value in zip(
                    column.expanded_indexes,
                    distributed,
                    strict=False,
                ):
                    normalized[target_index] = value
                continue

            if column.kind == "notes":
                pending_notes.append(cell)
                continue

            if column.kind == "task_notes":
                if pending_tasks or self._looks_note_like(cell):
                    pending_notes.append(cell)
                else:
                    pending_tasks.append(cell)
                continue

            pending_tasks.append(cell)

        self._assign_task_and_notes(
            normalized=normalized,
            pending_tasks=pending_tasks,
            pending_notes=pending_notes,
            plan=plan,
        )
        return normalized

    @staticmethod
    def _assign_task_and_notes(
        *,
        normalized: list[str],
        pending_tasks: list[str],
        pending_notes: list[str],
        plan: _HeaderPlan,
    ) -> None:
        if plan.task_index is not None and pending_tasks:
            normalized[plan.task_index] = pending_tasks[0]
            pending_tasks = pending_tasks[1:]
        if plan.notes_index is not None:
            notes_values = [*pending_notes, *pending_tasks]
            if notes_values:
                normalized[plan.notes_index] = " | ".join(notes_values)

    def _distribute_schedule_cell(
        self,
        value: str,
        *,
        target_count: int,
    ) -> list[str] | None:
        if target_count <= 0:
            return None
        cleaned = normalize_cell(value)
        if not cleaned:
            return [""] * target_count
        if looks_boolean_marker(cleaned):
            return ["x"] * target_count

        tokens = [
            token
            for token in cleaned.replace("/", " ").replace(",", " ").replace(";", " ").split()
            if token
        ]
        if tokens and all(looks_boolean_marker(token) for token in tokens):
            padded = list(tokens[:target_count])
            if len(padded) < target_count:
                padded.extend([""] * (target_count - len(padded)))
            return padded
        return None

    @staticmethod
    def _looks_note_like(value: str) -> bool:
        normalized = normalize_cell(value).casefold()
        return any(marker in normalized for marker in _NOTE_VALUE_MARKERS)

    def _schedule_labels(self, header: str) -> tuple[str, ...]:
        normalized = normalize_cell(header).casefold()
        if not normalized:
            return ()
        if normalized in SCHEDULE_INTERVAL_LABELS:
            return (SCHEDULE_INTERVAL_LABELS[normalized],)
        if normalized.startswith("every ") or normalized.endswith(" hours"):
            return (header,)

        tokens = [
            token
            for token in normalized.replace("/", " ").replace(",", " ").replace(";", " ").split()
            if token
        ]
        if not tokens or not all(token in SCHEDULE_INTERVAL_LABELS for token in tokens):
            return ()
        labels = [SCHEDULE_INTERVAL_LABELS[token] for token in tokens]
        return tuple(dict.fromkeys(labels))
