from src.domain.extraction import ExtractionResult, Procedure, ProcedureType

from .merge_support import merge_common_fields, normalize_for_dedup_key


def merge_procedures(partial_results: list[ExtractionResult]) -> list[Procedure]:
    merged: dict[tuple[str, ...], Procedure] = {}
    for result in partial_results:
        for item in result.procedures:
            key = (
                normalize_for_dedup_key(item.title),
                normalize_for_dedup_key(item.component_name),
            )
            if key not in merged:
                merged[key] = item
                continue
            _merge_procedure(merged[key], item)
    return list(merged.values())


def _merge_procedure(current: Procedure, candidate: Procedure) -> None:
    current.steps = current.steps or candidate.steps
    current.component_name = current.component_name or candidate.component_name
    current.equipment_id = current.equipment_id or candidate.equipment_id
    if current.procedure_type == ProcedureType.UNKNOWN:
        current.procedure_type = candidate.procedure_type
    current.source_metadata = current.source_metadata or candidate.source_metadata
    merge_common_fields(current, candidate)
