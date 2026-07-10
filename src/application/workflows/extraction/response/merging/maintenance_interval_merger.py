from src.domain.extraction import ExtractionResult, MaintenanceInterval

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_maintenance_intervals(
    partial_results: list[ExtractionResult],
) -> list[MaintenanceInterval]:
    merged: dict[tuple[str, ...], MaintenanceInterval] = {}
    for result in partial_results:
        for item in result.maintenance_intervals:
            key = (
                normalize_for_dedup_key(item.interval),
                normalize_for_dedup_key(item.component_name),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_maintenance_interval(merged[key], item)
    return list(merged.values())


def _merge_maintenance_interval(
    current: MaintenanceInterval,
    candidate: MaintenanceInterval,
) -> None:
    current.maintenance_task_id = (
        current.maintenance_task_id or candidate.maintenance_task_id
    )
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
