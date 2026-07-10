from src.domain.extraction import EquipmentInfo, ExtractionResult

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_equipment(partial_results: list[ExtractionResult]) -> list[EquipmentInfo]:
    merged: dict[tuple[str, ...], EquipmentInfo] = {}
    for result in partial_results:
        for item in result.equipment:
            key = (
                normalize_for_dedup_key(item.name),
                normalize_for_dedup_key(item.model_number),
                normalize_for_dedup_key(item.serial_number),
                normalize_for_dedup_key(item.manufacturer_name),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_equipment_info(merged[key], item)
    return list(merged.values())


def _merge_equipment_info(current: EquipmentInfo, candidate: EquipmentInfo) -> None:
    current.name = current.name or candidate.name
    current.model_number = current.model_number or candidate.model_number
    current.serial_number = current.serial_number or candidate.serial_number
    current.manufacturer_name = current.manufacturer_name or candidate.manufacturer_name
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
