PROCEDURE_TYPE_VALUES = (
    "maintenance|inspection|replacement|repair|installation|commissioning|"
    "operation|startup|shutdown|calibration|testing|troubleshooting|safety|"
    "cleaning_flushing|assembly_disassembly|storage_preservation|"
    "decommissioning|unknown"
)

PROCEDURE_SCHEMA_TEXT = (
    '  "procedures": [\n'
    "    {\n"
    '      "title": "<string>",\n'
    f'      "procedure_type": "<one of: {PROCEDURE_TYPE_VALUES}>",\n'
    '      "steps": ["<string>", "..."],\n'
    '      "component_name": "<string or null>",\n'
    '      "equipment_reference": "<string or null>",\n'
    '      "source_chunk_id": "<chunk id or null>",\n'
    '      "confidence_score": <float between 0 and 1 or null>,\n'
    '      "requires_human_review": <true or false>\n'
    "    }\n"
    "  ]\n"
)

PROCEDURE_GUIDANCE = (
    "Extract ordered, multi-step instructions (installation, operation, "
    "troubleshooting, disassembly, etc.) as a procedure with an ordered "
    '"steps" array, one string per step, in the order they appear in the '
    "text. Do not extract single-sentence maintenance tasks here — those "
    "belong in maintenance_tasks. A procedure must be linked to the "
    "equipment it is performed on: set equipment_reference to the name or "
    "model of that equipment if mentioned nearby, or null if it cannot be "
    "determined from the text. Classify the procedure's purpose into "
    f'procedure_type, one of: {PROCEDURE_TYPE_VALUES}. Use "unknown" only '
    "if none of the other categories fit.\n"
)
