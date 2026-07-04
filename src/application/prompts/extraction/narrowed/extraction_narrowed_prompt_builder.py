from src.application.prompts.common import PromptMetadata
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.prompts.extraction.common.prompt_text_utils import (
    allowed_chunk_ids,
    build_correction_notice,
    format_chunk_blocks,
)
from src.application.prompts.extraction.common.shared_extraction_rules import (
    SHARED_EXTRACTION_RULES,
)
from src.application.prompts.extraction.equipment.equipment_extraction_examples import (
    EQUIPMENT_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.equipment.equipment_extraction_schema import (
    EQUIPMENT_GUIDANCE,
    EQUIPMENT_SCHEMA_TEXT,
)
from src.application.prompts.extraction.identifiers.identifier_extraction_examples import (
    IDENTIFIER_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.identifiers.identifier_extraction_schema import (
    identifier_schema_text,
    identifier_type_guidance,
)
from src.application.prompts.extraction.maintenance.maintenance_interval_extraction_examples import (
    MAINTENANCE_INTERVAL_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.maintenance.maintenance_interval_extraction_schema import (
    MAINTENANCE_INTERVAL_GUIDANCE,
    MAINTENANCE_INTERVAL_SCHEMA_TEXT,
)
from src.application.prompts.extraction.maintenance.maintenance_task_extraction_examples import (
    MAINTENANCE_TASK_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.maintenance.maintenance_task_extraction_schema import (
    MAINTENANCE_TASK_SCHEMA_TEXT,
)
from src.application.prompts.extraction.manufacturers.manufacturer_extraction_examples import (
    MANUFACTURER_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.manufacturers.manufacturer_extraction_schema import (
    MANUFACTURER_GUIDANCE,
    MANUFACTURER_SCHEMA_TEXT,
)
from src.application.prompts.extraction.procedures.procedure_extraction_examples import (
    PROCEDURE_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.procedures.procedure_extraction_schema import (
    PROCEDURE_GUIDANCE,
    PROCEDURE_SCHEMA_TEXT,
)
from src.application.prompts.extraction.safety.safety_warning_extraction_examples import (
    SAFETY_WARNING_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.safety.safety_warning_extraction_schema import (
    SAFETY_WARNING_GUIDANCE,
    SAFETY_WARNING_SCHEMA_TEXT,
)
from src.application.prompts.extraction.spare_parts.spare_part_extraction_examples import (
    SPARE_PART_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.spare_parts.spare_part_extraction_schema import (
    SPARE_PART_SCHEMA_TEXT,
)
from src.application.prompts.extraction.specifications.specification_extraction_examples import (
    SPECIFICATION_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.specifications.specification_extraction_schema import (
    SPECIFICATION_GUIDANCE,
    SPECIFICATION_SCHEMA_TEXT,
)
from src.application.prompts.extraction.suppliers.supplier_extraction_examples import (
    SUPPLIER_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.suppliers.supplier_extraction_schema import (
    SUPPLIER_GUIDANCE,
    SUPPLIER_SCHEMA_TEXT,
)
from src.application.prompts.extraction.troubleshooting.troubleshooting_extraction_examples import (
    TROUBLESHOOTING_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.troubleshooting.troubleshooting_extraction_schema import (
    TROUBLESHOOTING_GUIDANCE,
    TROUBLESHOOTING_SCHEMA_TEXT,
)
from src.domain.document import DocumentChunk

NARROWED_EXTRACTION_PROMPT_VERSION = "v1"

# Fixed order the legacy combined prompt used, preserved so a fully-narrowed
# (all-types) prompt renders identically to the legacy one.
_ORDERED_TYPES: tuple[ExtractionPromptType, ...] = (
    ExtractionPromptType.MAINTENANCE_TASK,
    ExtractionPromptType.SPARE_PART,
    ExtractionPromptType.EQUIPMENT,
    ExtractionPromptType.MANUFACTURER,
    ExtractionPromptType.SUPPLIER,
    ExtractionPromptType.PROCEDURE,
    ExtractionPromptType.SPECIFICATION,
    ExtractionPromptType.SAFETY_WARNING,
    ExtractionPromptType.MAINTENANCE_INTERVAL,
    ExtractionPromptType.TROUBLESHOOTING,
    ExtractionPromptType.IDENTIFIER,
)


def _identifier_guidance() -> str:
    return (
        "Identifier type guidance:\n"
        + identifier_type_guidance()
        + "A manufacturer made the item; a supplier sold, distributed, or "
        "provided the item but did not necessarily make it. Use the "
        "manufacturers list for the former and the suppliers list for the "
        "latter. If a chunk does not distinguish the two roles, prefer "
        "manufacturers.\n"
    )


_FAMILY_SCHEMA: dict[ExtractionPromptType, str] = {
    ExtractionPromptType.IDENTIFIER: identifier_schema_text(),
    ExtractionPromptType.MANUFACTURER: MANUFACTURER_SCHEMA_TEXT,
    ExtractionPromptType.SUPPLIER: SUPPLIER_SCHEMA_TEXT,
    ExtractionPromptType.EQUIPMENT: EQUIPMENT_SCHEMA_TEXT,
    ExtractionPromptType.SPARE_PART: SPARE_PART_SCHEMA_TEXT,
    ExtractionPromptType.SPECIFICATION: SPECIFICATION_SCHEMA_TEXT,
    ExtractionPromptType.MAINTENANCE_TASK: MAINTENANCE_TASK_SCHEMA_TEXT,
    ExtractionPromptType.MAINTENANCE_INTERVAL: MAINTENANCE_INTERVAL_SCHEMA_TEXT,
    ExtractionPromptType.PROCEDURE: PROCEDURE_SCHEMA_TEXT,
    ExtractionPromptType.SAFETY_WARNING: SAFETY_WARNING_SCHEMA_TEXT,
    ExtractionPromptType.TROUBLESHOOTING: TROUBLESHOOTING_SCHEMA_TEXT,
}

# SPARE_PART and MAINTENANCE_TASK have no dedicated guidance paragraph in
# their modular families — their schema field names are self-explanatory.
_FAMILY_GUIDANCE: dict[ExtractionPromptType, str] = {
    ExtractionPromptType.IDENTIFIER: _identifier_guidance(),
    ExtractionPromptType.MANUFACTURER: MANUFACTURER_GUIDANCE,
    ExtractionPromptType.SUPPLIER: SUPPLIER_GUIDANCE,
    ExtractionPromptType.EQUIPMENT: EQUIPMENT_GUIDANCE,
    ExtractionPromptType.SPECIFICATION: SPECIFICATION_GUIDANCE,
    ExtractionPromptType.MAINTENANCE_INTERVAL: MAINTENANCE_INTERVAL_GUIDANCE,
    ExtractionPromptType.PROCEDURE: PROCEDURE_GUIDANCE,
    ExtractionPromptType.SAFETY_WARNING: SAFETY_WARNING_GUIDANCE,
    ExtractionPromptType.TROUBLESHOOTING: TROUBLESHOOTING_GUIDANCE,
}

_FAMILY_EXAMPLE: dict[ExtractionPromptType, str] = {
    ExtractionPromptType.IDENTIFIER: IDENTIFIER_EXTRACTION_EXAMPLE,
    ExtractionPromptType.MANUFACTURER: MANUFACTURER_EXTRACTION_EXAMPLE,
    ExtractionPromptType.SUPPLIER: SUPPLIER_EXTRACTION_EXAMPLE,
    ExtractionPromptType.EQUIPMENT: EQUIPMENT_EXTRACTION_EXAMPLE,
    ExtractionPromptType.SPARE_PART: SPARE_PART_EXTRACTION_EXAMPLE,
    ExtractionPromptType.SPECIFICATION: SPECIFICATION_EXTRACTION_EXAMPLE,
    ExtractionPromptType.MAINTENANCE_TASK: MAINTENANCE_TASK_EXTRACTION_EXAMPLE,
    ExtractionPromptType.MAINTENANCE_INTERVAL: MAINTENANCE_INTERVAL_EXTRACTION_EXAMPLE,
    ExtractionPromptType.PROCEDURE: PROCEDURE_EXTRACTION_EXAMPLE,
    ExtractionPromptType.SAFETY_WARNING: SAFETY_WARNING_EXTRACTION_EXAMPLE,
    ExtractionPromptType.TROUBLESHOOTING: TROUBLESHOOTING_EXTRACTION_EXAMPLE,
}


class ExtractionNarrowedPromptBuilder:
    """
    Composes a combined extraction prompt covering only a requested subset
    of ExtractionPromptType families, by reusing the exact schema/guidance/
    example text each modular per-family builder (procedures/,
    troubleshooting/, safety/, etc.) already owns — no duplicated prompt
    copy. When requested_types covers every family, the output is
    equivalent to LegacyExtractionPromptBuilder's combined prompt (same
    families, same order), just assembled from the modular pieces instead
    of one hardcoded string.

    Does not implement the ExtractionPromptBuilder protocol used by
    EXTRACTION_PROMPT_REGISTRY (build() takes an extra required
    requested_types argument) — it is only ever called directly by
    ExtractionWorkflow when candidate narrowing is enabled.
    """

    prompt_version = NARROWED_EXTRACTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="narrowed_extraction",
        version=NARROWED_EXTRACTION_PROMPT_VERSION,
        task_type="extraction",
        model_type="llm",
        description=(
            "Extract only the semantic entity types ExtractionCandidateSelector "
            "flagged as plausible for this batch of chunks."
        ),
    )

    def build(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
        *,
        requested_types: frozenset[ExtractionPromptType],
        previous_error: str | None = None,
    ) -> str:
        ordered = [
            entity_type for entity_type in _ORDERED_TYPES if entity_type in requested_types
        ]
        schema_body = (
            ",\n".join(_FAMILY_SCHEMA[entity_type].rstrip("\n") for entity_type in ordered)
            + "\n"
        )
        guidance_body = "".join(
            _FAMILY_GUIDANCE[entity_type]
            for entity_type in ordered
            if entity_type in _FAMILY_GUIDANCE
        )
        examples_body = "".join(
            _FAMILY_EXAMPLE[entity_type]
            for entity_type in ordered
            if entity_type in _FAMILY_EXAMPLE
        )

        return (
            build_correction_notice(previous_error)
            + SHARED_EXTRACTION_RULES
            + "Use this schema:\n"
            "{\n"
            '  "confidence_score": <float between 0 and 1>,\n'
            '  "requires_human_review": <true or false>,\n'
            f"{schema_body}"
            "}\n"
            f"{guidance_body}"
            f"{examples_body}"
            f"Allowed chunk_id values (use one of these EXACTLY, or null): {allowed_chunk_ids(chunks)}\n"
            f"Document id: {document_id}\n"
            "Chunks:\n"
            f"{format_chunk_blocks(chunks)}"
        )
