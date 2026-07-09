CONTACT_POINT_SCHEMA_TEXT = (
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
    "  ]\n"
)

CONTACT_POINT_GUIDANCE = (
    "Contact points capture organization contact channels such as phone numbers, "
    "fax numbers, email addresses, and websites. When the chunk clearly ties a "
    "contact value to a manufacturer or supplier, set owner_name and "
    'owner_entity_type ("manufacturer" or "supplier"). If the owner is not '
    "clear from the chunk, use null instead of guessing.\n"
)
