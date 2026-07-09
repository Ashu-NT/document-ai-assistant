from src.application.prompts.common import PromptMetadata
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)

EXTRACTION_CANDIDATE_ROUTER_PROMPT_VERSION = "v1"

_CATEGORY_DESCRIPTIONS: dict[ExtractionPromptType, str] = {
    ExtractionPromptType.IDENTIFIER: (
        "part numbers, serial numbers, model numbers, drawing numbers, "
        "certificate numbers"
    ),
    ExtractionPromptType.MANUFACTURER: "who made an item",
    ExtractionPromptType.SUPPLIER: "who sold or distributed an item",
    ExtractionPromptType.CONTACT_POINT: (
        "contact details such as phone numbers, fax numbers, email addresses, "
        "or websites"
    ),
    ExtractionPromptType.EQUIPMENT: (
        "named pieces of equipment (name, model, serial)"
    ),
    ExtractionPromptType.SPARE_PART: (
        "replaceable parts (part number, description, quantity)"
    ),
    ExtractionPromptType.SPECIFICATION: "technical parameter/value pairs",
    ExtractionPromptType.MAINTENANCE_TASK: "a maintenance action to perform",
    ExtractionPromptType.MAINTENANCE_INTERVAL: (
        "how often a maintenance task recurs"
    ),
    ExtractionPromptType.PROCEDURE: "ordered multi-step instructions",
    ExtractionPromptType.SAFETY_WARNING: "hazards or cautionary notes",
    ExtractionPromptType.TROUBLESHOOTING: "symptom/cause/remedy entries",
}
_CATEGORIES_DOC = "\n".join(
    f"- {entity_type.value}: {description}"
    for entity_type, description in _CATEGORY_DESCRIPTIONS.items()
)


class ExtractionCandidateRouterPromptBuilder:
    """
    Prompt for ExtractionCandidateLLMRouter: given a single chunk whose
    ChunkType stayed GENERAL/UNKNOWN after deterministic classification (and
    its own LLM fallback), asks which semantic entity types are worth
    extracting from it. A multi-label chunk-level classification prompt,
    not a full document-chunks extraction prompt — deliberately does not
    implement the ExtractionPromptBuilder protocol used by the 11 entity
    extraction builders (build(document_id, chunks, previous_error=...)),
    so it is not registered in EXTRACTION_PROMPT_REGISTRY.
    """

    prompt_version = EXTRACTION_CANDIDATE_ROUTER_PROMPT_VERSION
    metadata = PromptMetadata(
        name="extraction_candidate_router",
        version=EXTRACTION_CANDIDATE_ROUTER_PROMPT_VERSION,
        task_type="classification",
        model_type="llm",
        description=(
            "Decide which semantic entity types are worth extracting from "
            "a chunk that deterministic classification could not resolve."
        ),
    )

    def build(self, content: str) -> str:
        return (
            "You are deciding which categories of information are worth "
            "extracting from a single chunk of a technical/maintenance "
            "document. Deterministic rules could not confidently classify "
            "this chunk.\n\n"
            "Categories:\n"
            f"{_CATEGORIES_DOC}\n\n"
            'Return JSON only, in the form {"candidate_types": '
            '["<category>", ...]}. Include only categories that plausibly '
            "apply to this chunk. Return an empty array if none apply.\n\n"
            "Chunk:\n"
            f"{content}\n"
        )
