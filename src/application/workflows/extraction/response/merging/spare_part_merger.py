from src.domain.extraction import ExtractionResult, SparePart

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_spare_parts(partial_results: list[ExtractionResult]) -> list[SparePart]:
    merged: dict[tuple[str, ...], SparePart] = {}
    for result in partial_results:
        for item in result.spare_parts:
            key = (
                normalize_for_dedup_key(item.part_number or item.description),
                normalize_for_dedup_key(item.manufacturer_name),
                normalize_for_dedup_key(item.component_name),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_spare_part(merged[key], item)
    return list(merged.values())


def _merge_spare_part(current: SparePart, candidate: SparePart) -> None:
    current.part_number = current.part_number or candidate.part_number
    current.description = current.description or candidate.description
    current.quantity = current.quantity or candidate.quantity
    current.component_name = current.component_name or candidate.component_name
    current.manufacturer_name = current.manufacturer_name or candidate.manufacturer_name
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
