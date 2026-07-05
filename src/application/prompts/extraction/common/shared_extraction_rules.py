from src.application.prompts.extraction.common.json_output_rules import (
    JSON_OUTPUT_RULES,
)
from src.application.prompts.extraction.common.provenance_rules import (
    PROVENANCE_RULES,
)

SHARED_EXTRACTION_RULES = (
    "You extract structured information from technical document chunks.\n"
    + JSON_OUTPUT_RULES
    + PROVENANCE_RULES
    + "- Do not invent values that are not explicitly present in the text.\n"
    + "- Only emit an array item when the required evidence fields for that entity are present.\n"
    + "- If an item is missing its required fields, omit the item entirely instead of returning a partial object.\n"
)
