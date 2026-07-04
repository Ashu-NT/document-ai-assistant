TROUBLESHOOTING_SCHEMA_TEXT = (
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
    "  ]\n"
)

TROUBLESHOOTING_GUIDANCE = (
    "Troubleshooting entries capture symptom/cause/remedy rows — these are "
    "frequently presented as a table with symptom, probable cause, and "
    "remedy columns; extract every row. symptom is the fault or problem "
    "description; cause is the probable cause if stated, else null; remedy "
    "is the corrective action if stated, else null. equipment_reference is "
    "the name or model of the equipment this entry applies to, matching an "
    "entry in the equipment list if mentioned nearby, or null.\n"
)
