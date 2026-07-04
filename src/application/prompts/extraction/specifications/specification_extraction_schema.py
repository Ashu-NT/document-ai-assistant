SPECIFICATION_SCHEMA_TEXT = (
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
    "  ]\n"
)

SPECIFICATION_GUIDANCE = (
    "Extract technical specifications as parameter/value pairs (e.g. "
    'parameter="Pressure rating", value="16", unit="bar"). Split the numeric '
    "value from its unit when both are present. Do not extract part numbers, "
    "maintenance intervals, or safety warnings here.\n"
)
