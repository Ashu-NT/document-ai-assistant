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
from src.application.prompts.extraction.troubleshooting.troubleshooting_extraction_examples import (
    TROUBLESHOOTING_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.troubleshooting.troubleshooting_extraction_schema import (
    TROUBLESHOOTING_GUIDANCE,
    TROUBLESHOOTING_SCHEMA_TEXT,
)
from src.domain.document import DocumentChunk

TROUBLESHOOTING_EXTRACTION_PROMPT_VERSION = "v1"


class TroubleshootingExtractionPromptBuilder:
    """Net-new: troubleshooting symptom/cause/remedy tables had no
    extraction behavior before this family existed. Prompt layer only —
    persistence lives in TroubleshootingEntry/TroubleshootingEntryORM."""

    prompt_version = TROUBLESHOOTING_EXTRACTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="troubleshooting_extraction",
        version=TROUBLESHOOTING_EXTRACTION_PROMPT_VERSION,
        task_type="extraction",
        model_type="llm",
        description="Extract troubleshooting symptom/cause/remedy entries from chunks.",
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
            f"{TROUBLESHOOTING_SCHEMA_TEXT}"
            "}\n"
            f"{TROUBLESHOOTING_GUIDANCE}"
            f"{TROUBLESHOOTING_EXTRACTION_EXAMPLE}"
            f"Allowed chunk_id values (use one of these EXACTLY, or null): {allowed_chunk_ids(chunks)}\n"
            f"Document id: {document_id}\n"
            "Chunks:\n"
            f"{format_chunk_blocks(chunks)}"
        )
