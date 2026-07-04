from __future__ import annotations

from src.application.prompts.common import PromptMetadata
from src.application.prompts.extraction.common.prompt_text_utils import (
    allowed_chunk_ids,
    build_correction_notice,
    format_chunk_blocks,
)
from src.application.prompts.extraction.common.shared_extraction_rules import (
    SHARED_EXTRACTION_RULES,
)
from src.application.prompts.extraction.manufacturers.manufacturer_extraction_examples import (
    MANUFACTURER_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.manufacturers.manufacturer_extraction_schema import (
    MANUFACTURER_GUIDANCE,
    MANUFACTURER_SCHEMA_TEXT,
)
from src.domain.document import DocumentChunk

MANUFACTURER_EXTRACTION_PROMPT_VERSION = "v1"


class ManufacturerExtractionPromptBuilder:
    prompt_version = MANUFACTURER_EXTRACTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="manufacturer_extraction",
        version=MANUFACTURER_EXTRACTION_PROMPT_VERSION,
        task_type="extraction",
        model_type="llm",
        description="Extract manufacturer names, websites, and countries from chunks.",
    )

    def build(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
        *,
        previous_error: str | None = None,
    ) -> str:
        return (
            build_correction_notice(previous_error)
            + SHARED_EXTRACTION_RULES
            + "Use this schema:\n"
            "{\n"
            '  "confidence_score": <float between 0 and 1>,\n'
            '  "requires_human_review": <true or false>,\n'
            f"{MANUFACTURER_SCHEMA_TEXT}"
            "}\n"
            f"{MANUFACTURER_GUIDANCE}"
            f"{MANUFACTURER_EXTRACTION_EXAMPLE}"
            f"Allowed chunk_id values (use one of these EXACTLY, or null): {allowed_chunk_ids(chunks)}\n"
            f"Document id: {document_id}\n"
            "Chunks:\n"
            f"{format_chunk_blocks(chunks)}"
        )
