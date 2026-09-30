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
    "roles - do not fill one with a value that belongs in another: "
    "name=explicit product/system name; model_number=explicit model/type "
    "designation (e.g. \"Model\", \"Type\", \"Model No.\"); "
    "serial_number=explicit serial/S/N designation; manufacturer_name=an "
    "organization explicitly identified as the manufacturer, not a "
    "copyright holder, publisher, or document owner. A document/project/"
    "order number is not a model or serial number unless explicitly given "
    "that role.\n"
)
