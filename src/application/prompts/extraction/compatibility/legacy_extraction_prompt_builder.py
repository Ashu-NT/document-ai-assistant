from src.application.prompts.common import PromptMetadata
from src.application.prompts.extraction.extraction_prompt_version import (
    IDENTIFIER_EXTRACTION_PROMPT_VERSION,
)
from src.domain.document import DocumentChunk


class LegacyExtractionPromptBuilder:
    """Preserves the exact pre-modularization combined prompt behavior.

    ExtractionWorkflow's one call site depends on this exact output shape
    (maintenance_tasks, spare_parts, equipment, manufacturers, suppliers,
    identifiers in a single call/response). Re-exported as
    ``IdentifierExtractionPromptBuilder`` from the package root so existing
    imports and call sites keep working unchanged. New code should use the
    per-family builders under identifiers/, manufacturers/, suppliers/, etc.
    via ExtractionPromptFactory instead.
    """

    prompt_version = IDENTIFIER_EXTRACTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="identifier_extraction",
        version=IDENTIFIER_EXTRACTION_PROMPT_VERSION,
        task_type="extraction",
        model_type="llm",
        description="Extract maintenance, spare-part, equipment, manufacturer, supplier, procedure, specification, safety-warning, maintenance-interval, and troubleshooting data from chunks.",
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
            '  "suppliers": [\n'
            "    {\n"
            '      "name": "<string>",\n'
            '      "website": "<string or null>",\n'
            '      "country": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "contact_points": [\n'
            "    {\n"
            '      "contact_type": "phone_number|fax_number|email_address|url|unknown",\n'
            '      "value": "<string>",\n'
            '      "label": "<string or null>",\n'
            '      "owner_name": "<string or null>",\n'
            '      "owner_entity_type": "manufacturer|supplier|null",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "procedures": [\n'
            "    {\n"
            '      "title": "<string>",\n'
            '      "procedure_type": "<one of: maintenance|inspection|replacement|'
            "repair|installation|commissioning|operation|startup|shutdown|"
            'calibration|testing|troubleshooting|safety|cleaning_flushing|'
            'assembly_disassembly|storage_preservation|decommissioning|unknown>",\n'
            '      "steps": ["<string>", "..."],\n'
            '      "component_name": "<string or null>",\n'
            '      "equipment_reference": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "specifications": [\n'
            "    {\n"
            '      "parameter": "<string>",\n'
            '      "value": "<string>",\n'
            '      "unit": "<string or null>",\n'
            '      "component_name": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "safety_warnings": [\n'
            "    {\n"
            '      "warning_type": "danger|warning|caution|note",\n'
            '      "message": "<string>",\n'
            '      "component_name": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "maintenance_intervals": [\n'
            "    {\n"
            '      "component_name": "<string or null>",\n'
            '      "interval": "<string>",\n'
            '      "task_reference": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "troubleshooting_entries": [\n'
            "    {\n"
            '      "symptom": "<string>",\n'
            '      "cause": "<string or null>",\n'
            '      "remedy": "<string or null>",\n'
            '      "component_name": "<string or null>",\n'
            '      "equipment_reference": "<string or null>",\n'
            '      "source_chunk_id": "<chunk id or null>",\n'
            '      "confidence_score": <float between 0 and 1 or null>,\n'
            '      "requires_human_review": <true or false>\n'
            "    }\n"
            "  ],\n"
            '  "identifiers": [\n'
            "    {\n"
            '      "raw_value": "<exact string as it appears in text>",\n'
            '      "identifier_type": "part_number|serial_number|model_number|certificate_number|drawing_number|component_code|manufacturer_name|supplier_name|unknown",\n'
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
            '- "manufacturer_name": Manufacturer or OEM names not captured in the manufacturers list.\n'
            '- "supplier_name": Supplier, vendor, or distributor names not captured in the suppliers list.\n'
            '- "unknown": Any identifier that does not fit the types above.\n'
            "A manufacturer made the item; a supplier sold, distributed, or provided the item "
            "but did not necessarily make it. Use the manufacturers list for the former and "
            "the suppliers list for the latter. If a chunk does not distinguish the two roles, "
            "prefer manufacturers.\n"
            "Contact points are organization contact channels such as phone numbers, fax numbers, "
            "email addresses, and websites. When a chunk clearly ties a contact value to a "
            'manufacturer or supplier, set owner_name and owner_entity_type ("manufacturer" or '
            '"supplier"). If the owner is unclear, use null instead of guessing.\n'
            "Procedures are ordered, multi-step instructions (installation, operation, "
            "troubleshooting, disassembly) — put each step as its own string in the steps "
            "array, in the order they appear. Do not put single-sentence maintenance tasks here. "
            "equipment_reference is the name or model of the equipment this procedure is "
            "performed on, matching an entry in the equipment list if one is mentioned nearby, "
            "or null. Classify the procedure's purpose into procedure_type, one of: "
            "maintenance, inspection, replacement, repair, installation, commissioning, "
            "operation, startup, shutdown, calibration, testing, troubleshooting, safety, "
            "cleaning_flushing, assembly_disassembly, storage_preservation, decommissioning. "
            'Use "unknown" only if none of the other categories fit.\n'
            "Specifications are technical parameter/value pairs (e.g. parameter=\"Pressure "
            "rating\", value=\"16\", unit=\"bar\") — split the numeric value from its unit.\n"
            "Safety warnings are explicit hazards or cautionary notes. warning_type severity: "
            '"danger" (immediate serious hazard), "warning" (potential serious hazard), '
            '"caution" (minor/moderate hazard), "note" (non-hazard advisory); default to '
            '"warning" if severity is not stated. message must be the warning text itself.\n'
            "Maintenance intervals are recurring schedules (e.g. \"every 1000 operating "
            "hours\") extracted as first-class entries independent of the maintenance_tasks "
            "array. task_reference is the title text of the related maintenance task if one "
            "is mentioned nearby, or null.\n"
            "Troubleshooting entries capture symptom/cause/remedy rows (these are frequently "
            "presented as a table with symptom, probable cause, and remedy columns — extract "
            "every row). symptom is the fault or problem description; cause is the probable "
            "cause if stated, else null; remedy is the corrective action if stated, else null. "
            "equipment_reference is the name or model of the equipment this entry applies to, "
            "matching an entry in the equipment list if mentioned nearby, or null.\n"
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
            "- For identifiers: only extract values not already captured in spare_parts, equipment, manufacturers, or suppliers.\n"
            "- Do not invent identifiers — only extract values explicitly present in the text.\n"
            "- Only emit an array item when the required evidence fields for that entity are present.\n"
            "- If an item is missing its required fields, omit the item entirely instead of returning a partial object.\n"
            "- For identifiers: if raw_value is missing, omit the item instead of returning only identifier_type.\n"
            '- Never use placeholder labels such as "Document ID" or "Chunk ID" unless that exact text is the real identifier value in the chunk.\n'
            "- For identifiers: do not emit menu names, chapter numbers, parameter labels, display-message text, or internal system ids such as chunk_* or doc_*; omit them instead.\n"
            "- For specifications: omit any item that does not include both parameter and value.\n"
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
        page_range = LegacyExtractionPromptBuilder._format_page_range(
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
