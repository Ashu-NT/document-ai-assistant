EQUIPMENT_SCHEMA_TEXT = (
    '  "equipment": [\n'
    "    {\n"
    '      "name": "<string or null>",\n'
    '      "model_number": "<string or null>",\n'
    '      "serial_number": "<string or null>",\n'
    '      "manufacturer_name": "<string or null>",\n'
    '      "source_chunk_id": "<chunk id or null>",\n'
    '      "confidence_score": <float between 0 and 1 or null>,\n'
    '      "requires_human_review": <true or false>\n'
    "    }\n"
    "  ]\n"
)

EQUIPMENT_GUIDANCE = (
    "Extract named pieces of equipment/machinery, not individual spare parts. "
    "manufacturer_name here is a plain text field for cross-referencing — it "
    "is not itself a manufacturers-list entry.\n"
    "name, model_number, serial_number, and manufacturer_name are different "
    "semantic roles - do not fill one field with a value that belongs in "
    "another just because no separate value is obvious:\n"
    "- name: the descriptive equipment/product/system name stated by the "
    "source. Do not copy model_number or serial_number into name merely "
    "because a separate descriptive name is not obvious - leave name null "
    "instead.\n"
    "- model_number: only a value explicitly functioning as a model, type, "
    "or model designation (e.g. labeled \"Model\", \"Type\", \"Model No.\").\n"
    "- serial_number: only a value explicitly functioning as a serial "
    "number (e.g. labeled \"Serial No.\", \"S/N\").\n"
    "- manufacturer_name: only an organization explicitly identified as the "
    "manufacturer of the equipment. Do not infer manufacturer solely from "
    "a copyright holder, publisher, document owner, brand mention, or "
    "legal boilerplate naming a company - that identifies who published or "
    "owns the documentation, not necessarily who manufactured the "
    "equipment described in it.\n"
    "Project numbers, order numbers, and document numbers are NOT serial "
    "numbers or model numbers unless the source text explicitly gives them "
    "that role - leave the corresponding field null rather than reusing a "
    "nearby project/order/document number.\n"
)
