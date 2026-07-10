from src.domain.extraction import ExtractionResult, SafetyWarning

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_safety_warnings(partial_results: list[ExtractionResult]) -> list[SafetyWarning]:
    merged: dict[str, SafetyWarning] = {}
    for result in partial_results:
        for item in result.safety_warnings:
            key = normalize_for_dedup_key(item.message)
            if key not in merged:
                merged[key] = item
                continue
            _merge_safety_warning(merged[key], item)
    return list(merged.values())


def _merge_safety_warning(current: SafetyWarning, candidate: SafetyWarning) -> None:
    current.component_name = current.component_name or candidate.component_name
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
