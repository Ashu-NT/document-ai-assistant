SAFETY_WARNING_SCHEMA_TEXT = (
    '  "safety_warnings": [\n'
    "    {\n"
    '      "warning_type": "danger|warning|caution|note",\n'
    '      "message": "<string>",\n'
    '      "component_name": "<string or null>",\n'
    '      "source_chunk_id": "<chunk id or null>",\n'
    '      "confidence_score": <float between 0 and 1 or null>,\n'
    '      "requires_human_review": <true or false>\n'
    "    }\n"
    "  ]\n"
)

SAFETY_WARNING_GUIDANCE = (
    "Extract explicit safety warnings, hazards, and cautionary notes. "
    'warning_type severity: "danger" (immediate serious hazard), "warning" '
    '(potential serious hazard), "caution" (minor/moderate hazard), "note" '
    "(non-hazard advisory). If severity is not stated or implied, use "
    '"warning" as the default. message must be the warning text itself, not '
    "a paraphrase of the surrounding procedure.\n"
)
