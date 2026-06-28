from src.application.prompts.classification.classification_prompt_version import (
    CHUNK_TYPE_PROMPT_VERSION,
)
from src.application.prompts.common import PromptMetadata
from src.domain.common import ChunkType
from src.domain.document import DocumentChunk

_CHUNK_TYPES_DOC = "\n".join(
    f"- {chunk_type.value}: {description}"
    for chunk_type, description in [
        (
            ChunkType.TECHNICAL_SPECIFICATION,
            "Technical specs, measurements, ratings, parameters",
        ),
        (
            ChunkType.MAINTENANCE_PROCEDURE,
            "Step-by-step maintenance or service instructions",
        ),
        (
            ChunkType.MAINTENANCE_INTERVAL,
            "Scheduled maintenance timing, service frequencies",
        ),
        (
            ChunkType.INSTALLATION_INSTRUCTION,
            "Installation, mounting, or assembly steps",
        ),
        (
            ChunkType.OPERATION_INSTRUCTION,
            "Operating procedures, startup/shutdown steps",
        ),
        (ChunkType.TROUBLESHOOTING, "Fault diagnosis, probable causes, remedies"),
        (ChunkType.SAFETY_WARNING, "Safety warnings, cautions, hazard notices"),
        (
            ChunkType.CERTIFICATION_INFO,
            "Certifications, approvals, ATEX/IECEx, compliance statements",
        ),
        (
            ChunkType.SPARE_PARTS_TABLE,
            "Spare parts lists, part numbers, ordering data",
        ),
        (ChunkType.DRAWING_REFERENCE, "Diagrams, figures, drawing references"),
        (ChunkType.OVERVIEW, "General overview or introduction to a product or section"),
        (ChunkType.GENERAL, "Content that does not clearly fit any other type"),
        (ChunkType.UNKNOWN, "Content that cannot be classified confidently"),
    ]
)


class ChunkTypePromptBuilder:
    prompt_version = CHUNK_TYPE_PROMPT_VERSION
    metadata = PromptMetadata(
        name="chunk_type_classification",
        version=CHUNK_TYPE_PROMPT_VERSION,
        task_type="classification",
        model_type="llm",
        description="Classify a chunk into a supported chunk type.",
    )

    def build(self, chunk: DocumentChunk) -> str:
        chunk_types = ", ".join(chunk_type.value for chunk_type in ChunkType)
        section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"
        page_range = self._format_page_range(
            chunk.source.page_start,
            chunk.source.page_end,
        )

        return (
            "You classify chunks from technical documents.\n"
            "Return JSON only.\n"
            "Use this schema:\n"
            "{\n"
            '  "label": "<chunk type>",\n'
            '  "confidence_score": <float between 0 and 1>,\n'
            '  "rationale": "<short explanation>",\n'
            '  "evidence": ["<evidence 1>", "<evidence 2>"]\n'
            "}\n"
            f"Allowed labels: {chunk_types}\n"
            "If the chunk does not match a supported label, use the label 'unknown'.\n"
            f"Chunk id: {chunk.chunk_id}\n"
            f"Document id: {chunk.document_id}\n"
            f"Section id: {chunk.section_id or 'N/A'}\n"
            f"Section path: {section_path}\n"
            f"Source pages: {page_range}\n"
            f"Chunk index: {chunk.chunk_index}/{chunk.chunk_total}\n"
            "Chunk content:\n"
            f"{chunk.content}"
        )

    def build_reclassification_prompt(
        self,
        *,
        content: str,
        section_path: list[str],
    ) -> str:
        path_text = " > ".join(section_path) if section_path else "(none)"
        return (
            "You are classifying a chunk from a technical product document.\n\n"
            f"Section path: {path_text}\n"
            f"Content (first 600 chars):\n{content[:1000]}\n\n"
            "Classify this chunk into exactly ONE of the types below.\n"
            "Reply with ONLY the type name (e.g. maintenance_interval). No explanation.\n\n"
            f"{_CHUNK_TYPES_DOC}\n\n"
            "Type:"
        )

    @staticmethod
    def _format_page_range(page_start: int | None, page_end: int | None) -> str:
        if page_start is None and page_end is None:
            return "N/A"
        if page_start == page_end:
            return str(page_start)
        if page_start is None:
            return str(page_end)
        if page_end is None:
            return str(page_start)
        return f"{page_start}-{page_end}"
