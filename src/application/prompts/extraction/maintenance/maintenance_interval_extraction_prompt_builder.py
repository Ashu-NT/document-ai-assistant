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
from src.application.prompts.extraction.maintenance.maintenance_interval_extraction_examples import (
    MAINTENANCE_INTERVAL_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.maintenance.maintenance_interval_extraction_schema import (
    MAINTENANCE_INTERVAL_GUIDANCE,
    MAINTENANCE_INTERVAL_SCHEMA_TEXT,
)
from src.domain.document import DocumentChunk

MAINTENANCE_INTERVAL_EXTRACTION_PROMPT_VERSION = "v1"


class MaintenanceIntervalExtractionPromptBuilder:
    """Net-new: extracts maintenance intervals as first-class entities,
    instead of the free-text ``interval`` field folded into maintenance
    tasks today. Prompt layer only — no domain/workflow wiring yet."""

    prompt_version = MAINTENANCE_INTERVAL_EXTRACTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="maintenance_interval_extraction",
        version=MAINTENANCE_INTERVAL_EXTRACTION_PROMPT_VERSION,
        task_type="extraction",
        model_type="llm",
        description="Extract recurring maintenance intervals as first-class entities from chunks.",
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
            f"{MAINTENANCE_INTERVAL_SCHEMA_TEXT}"
            "}\n"
            f"{MAINTENANCE_INTERVAL_GUIDANCE}"
            f"{MAINTENANCE_INTERVAL_EXTRACTION_EXAMPLE}"
            f"Allowed chunk_id values (use one of these EXACTLY, or null): {allowed_chunk_ids(chunks)}\n"
            f"Document id: {document_id}\n"
            "Chunks:\n"
            f"{format_chunk_blocks(chunks)}"
        )
