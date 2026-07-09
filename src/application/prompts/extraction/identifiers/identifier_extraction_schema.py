from __future__ import annotations

from src.domain.common.enums import IdentifierType

_IDENTIFIER_TYPE_DESCRIPTIONS: dict[IdentifierType, str] = {
    IdentifierType.PART_NUMBER: "P/N codes, part numbers, order numbers (e.g. HP-001, 4321-A).",
    IdentifierType.SERIAL_NUMBER: "S/N codes, unit serial numbers (e.g. SN-1234, SER-2024-001).",
    IdentifierType.MODEL_NUMBER: "Model designations for equipment (e.g. FWC-12, Model 500).",
    IdentifierType.PRODUCT_NAME: "Named products, systems, or equipment titles explicitly printed in the document (e.g. B-Control II control system).",
    IdentifierType.DRAWING_NUMBER: "DRG or DWG references (e.g. DRG-1234, DWG 500).",
    IdentifierType.COMPONENT_CODE: "Order codes, component codes, tag numbers (e.g. TAG-42, OC-8800).",
    IdentifierType.CERTIFICATE_NUMBER: "ISO, IEC, EN, ATEX, CERT numbers (e.g. ISO 9001, ATEX II 2G).",
    IdentifierType.MANUFACTURER_NAME: "Manufacturer or OEM names not captured in the manufacturers list.",
    IdentifierType.SUPPLIER_NAME: "Supplier, vendor, or distributor names not captured in the suppliers list.",
    IdentifierType.PHONE_NUMBER: "Business phone or telephone numbers explicitly printed in the document.",
    IdentifierType.FAX_NUMBER: "Fax numbers explicitly printed in the document.",
    IdentifierType.EMAIL_ADDRESS: "Email addresses explicitly printed in the document.",
    IdentifierType.URL: "Website URLs or web addresses explicitly printed in the document.",
    IdentifierType.UNKNOWN: "Any identifier that does not fit the types above.",
}


def identifier_type_pipe_values() -> str:
    """Pipe-delimited allowed values, generated from the enum so a new
    IdentifierType member appears here automatically instead of needing a
    hand-copied update."""
    return "|".join(member.value for member in IdentifierType)


def identifier_type_guidance() -> str:
    lines = []
    for member in IdentifierType:
        description = _IDENTIFIER_TYPE_DESCRIPTIONS.get(
            member, "No guidance registered for this identifier type yet."
        )
        lines.append(f'- "{member.value}": {description}\n')
    lines.append(
        "- Emit an identifier only when raw_value is present exactly in the chunk text.\n"
    )
    lines.append(
        "- If the identifier type is known but the exact raw_value is missing, omit the item instead of returning a partial object.\n"
    )
    lines.append(
        '- Never use placeholder labels such as "Document ID" or "Chunk ID" unless that exact text is the real identifier value in the chunk.\n'
    )
    lines.append(
        "- Do not emit menu names, chapter numbers, parameter labels, display-message text, or internal system ids such as chunk_* or doc_* as identifiers; omit them instead.\n"
    )
    return "".join(lines)


def identifier_schema_text() -> str:
    return (
        '  "identifiers": [\n'
        "    {\n"
        '      "raw_value": "<exact string as it appears in text>",\n'
        f'      "identifier_type": "{identifier_type_pipe_values()}",\n'
        '      "source_chunk_id": "<chunk id or null>",\n'
        '      "confidence_score": <float between 0 and 1 or null>,\n'
        '      "requires_human_review": <true or false>\n'
        "    }\n"
        "  ]\n"
    )
