from src.domain.extraction import ContactPoint, ContactPointType, ExtractionResult

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_contact_points(partial_results: list[ExtractionResult]) -> list[ContactPoint]:
    merged: dict[tuple[str, ...], ContactPoint] = {}
    for result in partial_results:
        for item in result.contact_points:
            key = (
                normalize_for_dedup_key(item.value),
                normalize_for_dedup_key(item.owner_name),
                normalize_for_dedup_key(
                    item.owner_entity_type.value
                    if item.owner_entity_type is not None
                    else None
                ),
                normalize_for_dedup_key(item.contact_type.value),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_contact_point(merged[key], item)
    return list(merged.values())


def _merge_contact_point(current: ContactPoint, candidate: ContactPoint) -> None:
    if current.contact_type == ContactPointType.UNKNOWN:
        current.contact_type = candidate.contact_type
    current.label = current.label or candidate.label
    current.owner_name = current.owner_name or candidate.owner_name
    current.owner_entity_type = current.owner_entity_type or candidate.owner_entity_type
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
