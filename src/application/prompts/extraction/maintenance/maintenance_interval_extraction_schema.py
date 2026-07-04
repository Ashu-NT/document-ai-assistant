MAINTENANCE_INTERVAL_SCHEMA_TEXT = (
    '  "maintenance_intervals": [\n'
    "    {\n"
    '      "component_name": "<string or null>",\n'
    '      "interval": "<string>",\n'
    '      "task_reference": "<string or null>",\n'
    '      "source_chunk_id": "<chunk id or null>",\n'
    '      "confidence_score": <float between 0 and 1 or null>,\n'
    '      "requires_human_review": <true or false>\n'
    "    }\n"
    "  ]\n"
)

MAINTENANCE_INTERVAL_GUIDANCE = (
    "Extract recurring maintenance intervals as first-class entries (e.g. "
    '"every 1000 operating hours", "annually", "every 6 months"), independent '
    "of the maintenance task they belong to. task_reference is a free-text "
    "reference to the related task title if one is mentioned nearby, or null.\n"
)
