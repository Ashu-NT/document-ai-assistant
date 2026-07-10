from src.domain.extraction import ExtractionResult, Supplier

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_suppliers(partial_results: list[ExtractionResult]) -> list[Supplier]:
    merged: dict[str, Supplier] = {}
    for result in partial_results:
        for item in result.suppliers:
            key = normalize_for_dedup_key(item.name)
            if key not in merged:
                merged[key] = item
                continue
            _merge_supplier(merged[key], item)
    return list(merged.values())


def _merge_supplier(current: Supplier, candidate: Supplier) -> None:
    current.website = current.website or candidate.website
    current.country = current.country or candidate.country
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
