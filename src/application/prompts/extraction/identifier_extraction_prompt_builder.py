from src.application.prompts.common import PromptMetadata
from src.application.prompts.extraction.extraction_prompt_version import (
    IDENTIFIER_EXTRACTION_PROMPT_VERSION,
)
from src.domain.document import DocumentChunk
from src.domain.extraction import ExtractionProfile


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
        profile: ExtractionProfile = ExtractionProfile.FULL,
    ) -> str:
        if profile is ExtractionProfile.RETRIEVAL_IDENTIFIERS:
            return self._build_retrieval_identifiers_prompt(document_id, chunks)
        return self._build_full_prompt(document_id, chunks)

    def _build_retrieval_identifiers_prompt(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
    ) -> str:
        chunk_blocks = "\n\n".join(self._format_chunk_block(chunk) for chunk in chunks)
        allowed_chunk_ids = ", ".join(chunk.chunk_id for chunk in chunks)

        return (
            "You extract retrieval-critical technical identifiers from document chunks.\n"
            "This includes identifiers that would normally appear inside maintenance "
            "tasks, spare parts, equipment, and manufacturer records — but you must "
            "output them as a single flat identifiers list, not as nested objects.\n"
            "Return JSON only. Do not return markdown. Do not return prose.\n"
            "Do not output maintenance_tasks, spare_parts, equipment, or manufacturers arrays.\n"
            "Output only confidence_score, requires_human_review, and identifiers.\n"
            "Use this schema:\n"
            "{\n"
            '  "confidence_score": <float between 0 and 1>,\n'
            '  "requires_human_review": <true or false>,\n'
            '  "identifiers": [\n'
            "    {\n"
            '      "raw_value": "<exact string as it appears in text>",\n'
            '      "identifier_type": "part_number|model_number|serial_number|equipment_id|equipment_name|component_code|tag_number|drawing_number|document_number|manufacturer_name|brand_name|system_name|task_component_name|maintenance_interval|maintenance_code|unknown",\n'
            '      "source_chunk_id": "<chunk id>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Identifier type guidance:\n"
            '- "part_number": P/N codes, part numbers, order numbers from spare parts (e.g. HP-001, 4321-A).\n'
            '- "model_number": Model designations for equipment (e.g. FWC-12, Model 500).\n'
            '- "serial_number": S/N codes, unit serial numbers (e.g. SN-1234, SER-2024-001).\n'
            '- "equipment_id": Tags or ids identifying a specific piece of equipment.\n'
            '- "equipment_name": The name of a piece of equipment (e.g. Hydraulic Pump, Macerator).\n'
            '- "component_code": Order codes, component codes from spare parts (e.g. TAG-42, OC-8800).\n'
            '- "tag_number": Instrument or asset tag numbers.\n'
            '- "drawing_number": DRG or DWG references (e.g. DRG-1234, DWG 500).\n'
            '- "document_number": Document, certificate, or reference numbers (e.g. ISO 9001, ATEX II 2G).\n'
            '- "manufacturer_name": Manufacturer or supplier names.\n'
            '- "brand_name": Brand names distinct from the manufacturer legal name.\n'
            '- "system_name": The name of a system or subsystem the equipment belongs to.\n'
            '- "task_component_name": The component a maintenance task applies to.\n'
            '- "maintenance_interval": A maintenance frequency or interval (e.g. "1000 operating hours", "Daily").\n'
            '- "maintenance_code": A coded reference for a maintenance task or procedure.\n'
            '- "unknown": Any identifier that does not fit the types above.\n'
            "Rules:\n"
            "- Use only the provided chunk content.\n"
            "- Do not extract generic PPE or generic nouns (e.g. \"safety helmet\", \"gloves\", "
            "\"cover\", \"pipe\", \"valve\") unless they are explicitly used as a part number, "
            "model number, tag, equipment name, manufacturer name, drawing number, document "
            "number, or coded component reference.\n"
            "- Every identifier MUST include a source_chunk_id that is one of the allowed chunk ids below.\n"
            "- source_chunk_id MUST be copied EXACTLY, character for character, from the allowed list below.\n"
            "- Never invent, abbreviate, guess, or reuse a chunk_id that is not in the allowed list below.\n"
            "- If no identifiers exist, return \"identifiers\": [].\n"
            "- An empty array MUST be written as [] exactly. Never write [null] or put null as an item inside an array.\n"
            "- Always include a top-level confidence_score. If uncertain, use 0.0 instead of null or omitting the field.\n"
            f"Allowed chunk_id values (use one of these EXACTLY): {allowed_chunk_ids}\n"
            f"Document id: {document_id}\n"
            "Chunks:\n"
            f"{chunk_blocks}"
        )

    def _build_full_prompt(
        self,
        document_id: str,
        chunks: list[DocumentChunk],
    ) -> str:
        chunk_blocks = "\n\n".join(self._format_chunk_block(chunk) for chunk in chunks)
        allowed_chunk_ids = ", ".join(chunk.chunk_id for chunk in chunks)

        return (
            "You extract structured information from technical document chunks.\n"
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
