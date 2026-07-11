from src.domain.extraction import ExtractionResult
from src.shared.collections.ordered_dedupe import unique_in_order
from src.shared.ids import IdGenerator, IdPrefix

from src.application.workflows.extraction.response.merging.contact_point_merger import (
    merge_contact_points,
)
from src.application.workflows.extraction.response.merging.equipment_merger import (
    merge_equipment,
)
from src.application.workflows.extraction.response.merging.identifier_merger import (
    merge_identifiers,
)
from src.application.workflows.extraction.response.merging.maintenance_interval_merger import (
    merge_maintenance_intervals,
)
from src.application.workflows.extraction.response.merging.manufacturer_merger import (
    merge_manufacturers,
)
from src.application.workflows.extraction.response.merging.procedure_merger import (
    merge_procedures,
)
from src.application.workflows.extraction.response.merging.safety_warning_merger import (
    merge_safety_warnings,
)
from src.application.workflows.extraction.response.merging.spare_part_merger import (
    merge_spare_parts,
)
from src.application.workflows.extraction.response.merging.specification_merger import (
    merge_specifications,
)
from src.application.workflows.extraction.response.merging.supplier_merger import (
    merge_suppliers,
)
from src.application.workflows.extraction.response.merging.task_merger import (
    merge_tasks,
)
from src.application.workflows.extraction.response.merging.troubleshooting_entry_merger import (
    merge_troubleshooting_entries,
)


class ExtractionResultMerger:
    def __init__(self, *, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def merge(
        self,
        *,
        document_id: str,
        partial_results: list[ExtractionResult],
    ) -> ExtractionResult:
        merged_tasks = merge_tasks(partial_results)
        merged_parts = merge_spare_parts(partial_results)
        merged_equipment = merge_equipment(partial_results)
        merged_manufacturers = merge_manufacturers(partial_results)
        merged_suppliers = merge_suppliers(partial_results)
        merged_contact_points = merge_contact_points(partial_results)
        merged_procedures = merge_procedures(partial_results)
        merged_specifications = merge_specifications(partial_results)
        merged_safety_warnings = merge_safety_warnings(partial_results)
        merged_maintenance_intervals = merge_maintenance_intervals(partial_results)
        merged_troubleshooting_entries = merge_troubleshooting_entries(partial_results)
        merged_identifiers = merge_identifiers(partial_results)
        source_chunk_ids = unique_in_order(
            chunk_id
            for result in partial_results
            for chunk_id in result.source_chunk_ids
        )
        confidences = [
            result.confidence_score
            for result in partial_results
            if result.confidence_score is not None
        ]
        confidence_score = (
            sum(confidences) / len(confidences)
            if confidences
            else 0.0
        )

        return ExtractionResult(
            extraction_id=self.id_generator.new_id(IdPrefix.EXTRACTION),
            document_id=document_id,
            maintenance_tasks=merged_tasks,
            spare_parts=merged_parts,
            equipment=merged_equipment,
            manufacturers=merged_manufacturers,
            suppliers=merged_suppliers,
            contact_points=merged_contact_points,
            procedures=merged_procedures,
            specifications=merged_specifications,
            safety_warnings=merged_safety_warnings,
            maintenance_intervals=merged_maintenance_intervals,
            troubleshooting_entries=merged_troubleshooting_entries,
            extracted_identifiers=merged_identifiers,
            source_chunk_ids=source_chunk_ids,
            confidence_score=confidence_score,
            requires_human_review=any(
                result.requires_human_review
                for result in partial_results
            ),
        )
