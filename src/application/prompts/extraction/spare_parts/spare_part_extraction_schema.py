SPARE_PART_SCHEMA_TEXT = (
    '  "spare_parts": [\n'
    "    {\n"
    '      "part_number": "<string or null>",\n'
    '      "description": "<string or null>",\n'
    '      "quantity": "<string or null>",\n'
    '      "component_name": "<string or null>",\n'
    '      "manufacturer_name": "<string or null>",\n'
    '      "source_chunk_id": "<chunk id or null>",\n'
    '      "confidence_score": <float between 0 and 1 or null>,\n'
    '      "requires_human_review": <true or false>\n'
    "    }\n"
    "  ]\n"
)

SPARE_PART_GUIDANCE = (
    "A SparePart is a replaceable component/item intended as a part used "
    "in or for the equipment - not a technical parameter/value (that is a "
    "Specification) and not equipment used to perform work. Do not "
    "classify tools, special tools, measuring equipment, lifting "
    "equipment, torque tools, or generic consumables/materials as "
    "SparePart solely because they occur in a table titled something like "
    '"Special tools, Material, Spare parts". Classify an item as SparePart '
    "only when the source semantics indicate it is a replaceable "
    "component/part associated with the equipment. If an item is clearly "
    "a tool or material and does not fit any other entity here, omit it "
    "rather than force-fitting it into spare_parts.\n"
)
