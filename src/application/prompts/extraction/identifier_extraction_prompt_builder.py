from src.application.prompts.common import PromptMetadata
from src.application.prompts.extraction.extraction_prompt_version import (
    IDENTIFIER_EXTRACTION_PROMPT_VERSION,
)
from src.domain.document import DocumentChunk


class IdentifierExtractionPromptBuilder:
    prompt_version = IDENTIFIER_EXTRACTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="identifier_extraction",
        version=IDENTIFIER_EXTRACTION_PROMPT_VERSION,
        task_type="extraction",
        model_type="llm",
        description="Extract maintenance, spare-part, equipment, and manufacturer data from chunks.",
    )

    def build(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
        *,
        previous_error: str | None = None,
    ) -> str:
        chunk_blocks = "\n\n".join(self._format_chunk_block(chunk) for chunk in chunks)
        allowed_chunk_ids = ", ".join(chunk.chunk_id for chunk in chunks)
        correction_notice = self._build_correction_notice(previous_error)

        return (
            correction_notice
            + "You extract structured information from technical document chunks.\n"
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
            "  ],\n"
            '  "identifiers": [\n'
            "    {\n"
            '      "raw_value": "<exact string as it appears in text>",\n'
            '      "identifier_type": "part_number|serial_number|model_number|certificate_number|drawing_number|component_code|manufacturer_name|unknown",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Identifier type guidance:\n"
            '- "part_number": P/N codes, part numbers, order numbers (e.g. HP-001, 4321-A).\n'
            '- "serial_number": S/N codes, unit serial numbers (e.g. SN-1234, SER-2024-001).\n'
            '- "model_number": Model designations for equipment (e.g. FWC-12, Model 500).\n'
            '- "certificate_number": ISO, IEC, EN, ATEX, CERT numbers (e.g. ISO 9001, ATEX II 2G).\n'
            '- "drawing_number": DRG or DWG references (e.g. DRG-1234, DWG 500).\n'
            '- "component_code": Order codes, component codes, tag numbers (e.g. TAG-42, OC-8800).\n'
            '- "manufacturer_name": Manufacturer or supplier names not captured in the manufacturers list.\n'
            '- "unknown": Any identifier that does not fit the types above.\n'
            "Rules:\n"
            "- Use only the provided chunk content.\n"
            "- Use only the provided chunk ids when setting source_chunk_id.\n"
            "- source_chunk_id MUST be copied EXACTLY, character for character, from the allowed list below.\n"
            "- Never invent, abbreviate, guess, or reuse a chunk_id that is not in the allowed list below.\n"
            "- If you are not sure which chunk a value came from, use null for source_chunk_id instead of guessing.\n"
            "- Return empty arrays when nothing is found.\n"
            "- Do not return empty placeholder objects inside arrays. Use [] instead of objects whose fields are null, blank, N/A, or not available.\n"
            "- An empty array MUST be written as [] exactly. Never write [null] or put null as an item inside an array.\n"
            "- Always include a top-level confidence_score. If uncertain, use 0.0 instead of null or omitting the field.\n"
            "- Use null for unknown optional values.\n"
            "- For identifiers: only extract values not already captured in spare_parts, equipment, or manufacturers.\n"
            "- Do not invent identifiers — only extract values explicitly present in the text.\n"
            f"Allowed chunk_id values (use one of these EXACTLY, or null): {allowed_chunk_ids}\n"
            f"Document id: {document_id}\n"
            "Chunks:\n"
            f"{chunk_blocks}"
        )

    @staticmethod
    def _build_correction_notice(previous_error: str | None) -> str:
        if not previous_error:
            return ""

        return (
            "Your previous response was rejected because it did not match the "
            f"required schema: {previous_error}\n"
            "Fix this specific problem and return a corrected JSON response that "
            "matches the schema exactly.\n\n"
        )

    @staticmethod
    def _format_chunk_block(chunk: DocumentChunk) -> str:
        section_path = " > ".join(chunk.section_path) if chunk.section_path else "N/A"
        page_range = IdentifierExtractionPromptBuilder._format_page_range(
            chunk.source.page_start,
            chunk.source.page_end,
        )

        return (
            f"- Chunk id: {chunk.chunk_id}\n"
            f"  Section path: {section_path}\n"
            f"  Source pages: {page_range}\n"
            f"  Chunk index: {chunk.chunk_index}/{chunk.chunk_total}\n"
            "  Content:\n"
            f"  {chunk.content}"
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
