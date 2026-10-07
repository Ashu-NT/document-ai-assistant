MAINTENANCE_TASK_SCHEMA_TEXT = (
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
    "  ]\n"
)

MAINTENANCE_TASK_GUIDANCE = (
    "When a structured table row has its own component/equipment/item/"
    "assembly/system field identifying what the row's task applies to, "
    "copy that explicit field into component_name - prefer it over "
    "inferring a component from the task text itself, even when the same "
    "value repeats across several consecutive rows. Do not invent "
    "component_name when the source provides none.\n"
)
