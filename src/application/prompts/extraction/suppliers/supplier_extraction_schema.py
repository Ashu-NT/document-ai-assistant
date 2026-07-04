SUPPLIER_SCHEMA_TEXT = (
    '  "suppliers": [\n'
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

SUPPLIER_GUIDANCE = (
    "A supplier sold, distributed, or provided the item but did not "
    "necessarily make it. If a chunk describes the company that manufactured "
    "the item instead, that is a manufacturer, not a supplier — do not list "
    "it here. If a chunk does not distinguish the two roles, do not guess; "
    "omit it from this list.\n"
)
