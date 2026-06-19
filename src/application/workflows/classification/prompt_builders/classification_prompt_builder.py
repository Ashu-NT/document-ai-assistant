from src.domain.common import ChunkType, DocumentType
from src.domain.document import Document, DocumentChunk


class ClassificationPromptBuilder:
    prompt_version = "v1"

    def build_document_classification_prompt(
        self,
        document: Document,
    ) -> str:
        document_types = ", ".join(document_type.value for document_type in DocumentType)
        title = document.title or "N/A"
        language = document.language or "N/A"
        page_count = document.statistics.page_count or "N/A"

        return (
            "You classify technical documents using the provided metadata.\n"
            "Return JSON only.\n"
            "Use this schema:\n"
            "{\n"
            '  "label": "<document type>",\n'
            '  "confidence_score": <float between 0 and 1>,\n'
            '  "rationale": "<short explanation>",\n'
            '  "evidence": ["<evidence 1>", "<evidence 2>"]\n'
            "}\n"
            f"Allowed labels: {document_types}\n"
            "If the metadata is insufficient, use the label 'unknown'.\n"
            f"Document id: {document.document_id}\n"
            f"File name: {document.file_name}\n"
            f"File path: {document.file_path}\n"
            f"Title: {title}\n"
            f"Language: {language}\n"
            f"Page count: {page_count}\n"
            f"Element count: {document.statistics.element_count}\n"
            f"Section count: {document.statistics.section_count}\n"
            f"Chunk count: {document.statistics.chunk_count}\n"
            f"Table count: {document.statistics.table_count}\n"
            f"Picture count: {document.statistics.picture_count}"
        )

    def build_chunk_classification_prompt(
        self,
        chunk: DocumentChunk,
    ) -> str:
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
