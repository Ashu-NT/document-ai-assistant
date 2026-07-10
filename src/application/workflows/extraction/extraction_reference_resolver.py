from __future__ import annotations

from src.domain.extraction import EquipmentInfo, MaintenanceTask

# Cross-entity reference resolution -- matching an LLM-provided free-text
# reference (e.g. a maintenance task's title, an equipment's name/model
# number) against already-built sibling entities from the same batch, split
# out of extraction_workflow.py. Each resolver tries an exact
# (normalized-case) match first, then falls back to a substring match in
# either direction, exactly as before.


def resolve_maintenance_task_id(
    task_reference: str | None,
    maintenance_tasks: list[MaintenanceTask],
) -> str | None:
    if not task_reference:
        return None
    normalized_reference = task_reference.strip().lower()
    for task in maintenance_tasks:
        if task.title and task.title.strip().lower() == normalized_reference:
            return task.task_id
    for task in maintenance_tasks:
        normalized_title = (task.title or "").strip().lower()
        if normalized_title and (
            normalized_reference in normalized_title
            or normalized_title in normalized_reference
        ):
            return task.task_id
    return None


def resolve_equipment_id(
    equipment_reference: str | None,
    equipment: list[EquipmentInfo],
) -> str | None:
    if not equipment_reference:
        return None
    normalized_reference = equipment_reference.strip().lower()
    for item in equipment:
        candidates = (item.name, item.model_number)
        if any(
            candidate and candidate.strip().lower() == normalized_reference
            for candidate in candidates
        ):
            return item.equipment_id
    for item in equipment:
        candidates = (item.name, item.model_number)
        for candidate in candidates:
            normalized_candidate = (candidate or "").strip().lower()
            if normalized_candidate and (
                normalized_reference in normalized_candidate
                or normalized_candidate in normalized_reference
            ):
                return item.equipment_id
    return None
