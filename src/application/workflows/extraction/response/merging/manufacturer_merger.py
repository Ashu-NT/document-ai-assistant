from src.domain.extraction import ExtractionResult, Manufacturer

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_manufacturers(partial_results: list[ExtractionResult]) -> list[Manufacturer]:
    merged: dict[str, Manufacturer] = {}
    for result in partial_results:
        for item in result.manufacturers:
            key = normalize_for_dedup_key(item.name)
            if key not in merged:
                merged[key] = item
                continue
            _merge_manufacturer(merged[key], item)
    return list(merged.values())


def _merge_manufacturer(current: Manufacturer, candidate: Manufacturer) -> None:
    current.website = current.website or candidate.website
    current.country = current.country or candidate.country
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
