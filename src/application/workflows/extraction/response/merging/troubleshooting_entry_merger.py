from src.domain.extraction import ExtractionResult, TroubleshootingEntry

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_troubleshooting_entries(
    partial_results: list[ExtractionResult],
) -> list[TroubleshootingEntry]:
    merged: dict[tuple[str, ...], TroubleshootingEntry] = {}
    for result in partial_results:
        for item in result.troubleshooting_entries:
            key = (
                normalize_for_dedup_key(item.symptom),
                normalize_for_dedup_key(item.component_name),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_troubleshooting_entry(merged[key], item)
    return list(merged.values())


def _merge_troubleshooting_entry(
    current: TroubleshootingEntry,
    candidate: TroubleshootingEntry,
) -> None:
    current.cause = current.cause or candidate.cause
    current.remedy = current.remedy or candidate.remedy
    current.component_name = current.component_name or candidate.component_name
    current.equipment_id = current.equipment_id or candidate.equipment_id
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
