SPECIFICATION_SCHEMA_TEXT = (
    '  "specifications": [\n'
    "    {\n"
    '      "parameter": "<string>",\n'
    '      "value": "<string>",\n'
    '      "unit": "<string or null>",\n'
    '      "component_name": "<string or null>",\n'
    '      "source_chunk_id": "<chunk id or null>",\n'
    '      "confidence_score": <float between 0 and 1 or null>,\n'
    '      "requires_human_review": <true or false>\n'
    "    }\n"
    "  ]\n"
)

SPECIFICATION_GUIDANCE = (
    "Extract technical specifications as parameter/value pairs (e.g. "
    'parameter="Pressure rating", value="16", unit="bar"). Split the numeric '
    "value from its unit when both are present. Do not extract part numbers, "
    "maintenance intervals, or safety warnings here. Omit any specification "
    "item that does not include both parameter and value.\n"
    "A Specification is a technical parameter/value/property describing the "
    "equipment or a component - for example: capacity, pressure, voltage, "
    "power, dimensions, or a temperature/range, each expressed as a "
    "value with an optional unit. A SparePart is instead a replaceable "
    "component/item intended as a part used in or for the equipment. A "
    "technical-data table containing parameter/value rows must not be "
    "converted into SparePart entries merely because its cells contain "
    "labels, numbers, or units - a parameter label such as capacity, "
    "voltage, or power is not a part number.\n"
)
