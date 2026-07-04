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
from src.application.prompts.extraction.identifiers.identifier_extraction_examples import (
    IDENTIFIER_EXTRACTION_EXAMPLE,
)
from src.application.prompts.extraction.identifiers.identifier_extraction_schema import (
    identifier_schema_text,
    identifier_type_guidance,
)
from src.domain.document import DocumentChunk

IDENTIFIER_EXTRACTION_PROMPT_VERSION = "v1"


class IdentifierExtractionPromptBuilder:
    """Modular, identifier-only prompt builder.

    Distinct from the package root's ``IdentifierExtractionPromptBuilder``
    (the legacy combined builder) — that name is preserved at the package
    root purely for import-path backward compatibility and points at
    ``compatibility.LegacyExtractionPromptBuilder`` instead of this class.
    """

    prompt_version = IDENTIFIER_EXTRACTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="identifier_extraction_modular",
        version=IDENTIFIER_EXTRACTION_PROMPT_VERSION,
        task_type="extraction",
        model_type="llm",
        description="Extract standalone identifiers (part/serial/model/certificate/drawing/component codes) from chunks.",
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
            f"{identifier_schema_text()}"
            "}\n"
            "Identifier type guidance:\n"
            f"{identifier_type_guidance()}"
            "- Do not invent identifiers — only extract values explicitly present in the text.\n"
            f"{IDENTIFIER_EXTRACTION_EXAMPLE}"
            f"Allowed chunk_id values (use one of these EXACTLY, or null): {allowed_chunk_ids(chunks)}\n"
            f"Document id: {document_id}\n"
            "Chunks:\n"
            f"{format_chunk_blocks(chunks)}"
        )
