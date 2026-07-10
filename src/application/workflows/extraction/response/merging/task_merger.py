from src.domain.extraction import ExtractionResult, MaintenanceTask

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_tasks(partial_results: list[ExtractionResult]) -> list[MaintenanceTask]:
    merged: dict[tuple[str, ...], MaintenanceTask] = {}
    for result in partial_results:
        for item in result.maintenance_tasks:
            key = (
                normalize_for_dedup_key(item.title),
                normalize_for_dedup_key(item.interval),
                normalize_for_dedup_key(item.component_name or item.equipment_id),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_task(merged[key], item)
    return list(merged.values())


def _merge_task(current: MaintenanceTask, candidate: MaintenanceTask) -> None:
    current.description = current.description or candidate.description
    current.interval = current.interval or candidate.interval
    current.component_name = current.component_name or candidate.component_name
    current.equipment_id = current.equipment_id or candidate.equipment_id
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
