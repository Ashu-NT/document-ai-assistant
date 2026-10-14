from src.domain.extraction import ExtractionResult, MaintenanceTask

from .merge_support import merge_common_fields, normalize_for_dedup_key


def _dedup_key(item: MaintenanceTask) -> tuple:
    # A verified task_code (grounded against the canonical table evidence -
    # see MaintenanceTaskBuilder) is a stronger identity signal than title
    # text: two rows with different real codes are never the same
    # obligation even if the model paraphrases their titles identically,
    # and one row with two distinct obligations under the same code still
    # needs its own title to stay distinguishable. Falls back to the
    # original (title, interval, component) key whenever no verified code
    # is available on either side, preserving existing behavior there.
    if item.task_code:
        return (
            "code",
            item.document_id,
            normalize_for_dedup_key(item.task_code),
            normalize_for_dedup_key(item.title),
        )
    return (
        "fallback",
        item.document_id,
        normalize_for_dedup_key(item.title),
        normalize_for_dedup_key(item.interval),
        normalize_for_dedup_key(item.component_name or item.equipment_id),
    )


def merge_tasks(partial_results: list[ExtractionResult]) -> list[MaintenanceTask]:
    merged: dict[tuple, MaintenanceTask] = {}
    for result in partial_results:
        for item in result.maintenance_tasks:
            key = _dedup_key(item)
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
    current.task_code = current.task_code or candidate.task_code
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
