MANUFACTURER_SCHEMA_TEXT = (
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
)

MANUFACTURER_GUIDANCE = (
    "A manufacturer made the item. If a chunk mentions a company that sold, "
    "distributed, or provided the item without making it, that is a supplier, "
    "not a manufacturer — do not list it here. If a chunk does not distinguish "
    "the two roles, prefer manufacturer.\n"
)
