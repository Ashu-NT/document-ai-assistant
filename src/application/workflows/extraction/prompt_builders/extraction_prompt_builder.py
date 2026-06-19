from src.domain.document import DocumentChunk


class ExtractionPromptBuilder:
    prompt_version = "v1"

    def build_extraction_prompt(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
    ) -> str:
        chunk_blocks = "\n\n".join(
            self._format_chunk_block(chunk)
            for chunk in chunks
        )

        return (
            "You extract structured maintenance information from technical document chunks.\n"
            "Return JSON only.\n"
            "Use this schema:\n"
            "{\n"
            '  "confidence_score": <float between 0 and 1>,\n'
            '  "requires_human_review": <true or false>,\n'
            '  "maintenance_tasks": [\n'
            "    {\n"
            '      "title": "<string>",\n'
            '      "description": "<string or null>",\n'
            '      "interval": "<string or null>",\n'
            '      "component_name": "<string or null>",\n'
            '      "equipment_id": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "spare_parts": [\n'
            "    {\n"
            '      "part_number": "<string or null>",\n'
            '      "description": "<string or null>",\n'
            '      "quantity": "<string or null>",\n'
            '      "component_name": "<string or null>",\n'
            '      "manufacturer_name": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "equipment": [\n'
            "    {\n"
            '      "name": "<string or null>",\n'
            '      "model_number": "<string or null>",\n'
            '      "serial_number": "<string or null>",\n'
            '      "manufacturer_name": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "manufacturers": [\n'
            "    {\n"
            '      "name": "<string>",\n'
            '      "website": "<string or null>",\n'
            '      "country": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Rules:\n"
            "- Use only the provided chunk content.\n"
            "- Use only the provided chunk ids when setting source_chunk_id.\n"
            "- Return empty arrays when nothing is found.\n"
            "- Use null for unknown optional values.\n"
            f"Document id: {document_id}\n"
            "Chunks:\n"
            f"{chunk_blocks}"
        )

    @staticmethod
    def _format_chunk_block(chunk: DocumentChunk) -> str:
        section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"
        page_range = ExtractionPromptBuilder._format_page_range(chunk)

        return (
            f"- Chunk id: {chunk.chunk_id}\n"
            f"  Section path: {section_path}\n"
            f"  Source pages: {page_range}\n"
            f"  Chunk index: {chunk.chunk_index}/{chunk.chunk_total}\n"
            "  Content:\n"
            f"  {chunk.content}"
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
