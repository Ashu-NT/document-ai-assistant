from src.domain.extraction import ExtractionResult, Specification

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_specifications(partial_results: list[ExtractionResult]) -> list[Specification]:
    merged: dict[tuple[str, ...], Specification] = {}
    for result in partial_results:
        for item in result.specifications:
            key = (
                normalize_for_dedup_key(item.parameter),
                normalize_for_dedup_key(item.component_name),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_specification(merged[key], item)
    return list(merged.values())


def _merge_specification(current: Specification, candidate: Specification) -> None:
    current.unit = current.unit or candidate.unit
    current.component_name = current.component_name or candidate.component_name
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
