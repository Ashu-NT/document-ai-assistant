EQUIPMENT_SCHEMA_TEXT = (
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
    "  ]\n"
)

EQUIPMENT_GUIDANCE = (
    "Extract named pieces of equipment/machinery, not individual spare parts. "
    "manufacturer_name here is a plain text field for cross-referencing — it "
    "is not itself a manufacturers-list entry.\n"
)
