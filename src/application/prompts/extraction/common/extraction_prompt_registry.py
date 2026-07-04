from __future__ import annotations

from typing import Protocol

from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.prompts.extraction.equipment.equipment_extraction_prompt_builder import (
    EquipmentExtractionPromptBuilder,
)
from src.application.prompts.extraction.identifiers.identifier_extraction_prompt_builder import (
    IdentifierExtractionPromptBuilder,
)
from src.application.prompts.extraction.maintenance.maintenance_interval_extraction_prompt_builder import (
    MaintenanceIntervalExtractionPromptBuilder,
)
from src.application.prompts.extraction.maintenance.maintenance_task_extraction_prompt_builder import (
    MaintenanceTaskExtractionPromptBuilder,
)
from src.application.prompts.extraction.manufacturers.manufacturer_extraction_prompt_builder import (
    ManufacturerExtractionPromptBuilder,
)
from src.application.prompts.extraction.procedures.procedure_extraction_prompt_builder import (
    ProcedureExtractionPromptBuilder,
)
from src.application.prompts.extraction.safety.safety_warning_extraction_prompt_builder import (
    SafetyWarningExtractionPromptBuilder,
)
from src.application.prompts.extraction.spare_parts.spare_part_extraction_prompt_builder import (
    SparePartExtractionPromptBuilder,
)
from src.application.prompts.extraction.specifications.specification_extraction_prompt_builder import (
    SpecificationExtractionPromptBuilder,
)
from src.application.prompts.extraction.suppliers.supplier_extraction_prompt_builder import (
    SupplierExtractionPromptBuilder,
)
from src.domain.document import DocumentChunk


class ExtractionPromptBuilder(Protocol):
    prompt_version: str

    def build(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
        *,
        previous_error: str | None = None,
    ) -> str: ...


EXTRACTION_PROMPT_REGISTRY: dict[ExtractionPromptType, ExtractionPromptBuilder] = {
    ExtractionPromptType.IDENTIFIER: IdentifierExtractionPromptBuilder(),
    ExtractionPromptType.MANUFACTURER: ManufacturerExtractionPromptBuilder(),
    ExtractionPromptType.SUPPLIER: SupplierExtractionPromptBuilder(),
    ExtractionPromptType.EQUIPMENT: EquipmentExtractionPromptBuilder(),
    ExtractionPromptType.SPARE_PART: SparePartExtractionPromptBuilder(),
    ExtractionPromptType.SPECIFICATION: SpecificationExtractionPromptBuilder(),
    ExtractionPromptType.MAINTENANCE_TASK: MaintenanceTaskExtractionPromptBuilder(),
    ExtractionPromptType.MAINTENANCE_INTERVAL: MaintenanceIntervalExtractionPromptBuilder(),
    ExtractionPromptType.PROCEDURE: ProcedureExtractionPromptBuilder(),
    ExtractionPromptType.SAFETY_WARNING: SafetyWarningExtractionPromptBuilder(),
}


def get_builder(prompt_type: ExtractionPromptType) -> ExtractionPromptBuilder:
    try:
        return EXTRACTION_PROMPT_REGISTRY[prompt_type]
    except KeyError as exc:
        raise ValueError(
            f"No extraction prompt builder registered for {prompt_type!r}."
        ) from exc
