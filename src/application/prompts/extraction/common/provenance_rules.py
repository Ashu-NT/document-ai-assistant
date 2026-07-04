PROVENANCE_RULES = (
    "- Use only the provided chunk content.\n"
    "- Use only the provided chunk ids when setting source_chunk_id.\n"
    "- source_chunk_id MUST be copied EXACTLY, character for character, from "
    "the allowed list below.\n"
    "- Never invent, abbreviate, guess, or reuse a chunk_id that is not in the "
    "allowed list below.\n"
    "- If you are not sure which chunk a value came from, use null for "
    "source_chunk_id instead of guessing.\n"
)
