JSON_OUTPUT_RULES = (
    "Return JSON only.\n"
    "Rules:\n"
    "- Return empty arrays when nothing is found.\n"
    "- Do not return empty placeholder objects inside arrays. Use [] instead of "
    "objects whose fields are null, blank, N/A, or not available.\n"
    "- An empty array MUST be written as [] exactly. Never write [null] or put "
    "null as an item inside an array.\n"
    "- Always include a top-level confidence_score. If uncertain, use 0.0 "
    "instead of null or omitting the field.\n"
    "- Use null for unknown optional values.\n"
)
