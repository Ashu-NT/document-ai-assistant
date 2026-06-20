from src.domain.common import ChunkType
from src.domain.document import DocumentChunk


class ChunkClassificationPromptBuilder:
    prompt_version = "v1"

    def build(self, chunk: DocumentChunk) -> str:
        chunk_types = ", ".join(chunk_type.value for chunk_type in ChunkType)
        section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"
        page_range = self._format_page_range(chunk)

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

    @staticmethod
    def _format_page_range(chunk: DocumentChunk) -> str:
        page_start = chunk.source.page_start
        page_end = chunk.source.page_end

        if page_start is None and page_end is None:
            return "N/A"

        if page_start == page_end:
            return str(page_start)

        if page_start is None:
            return str(page_end)

        if page_end is None:
            return str(page_start)

        return f"{page_start}-{page_end}"
