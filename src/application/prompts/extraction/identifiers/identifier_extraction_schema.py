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
    """The single authoritative identifier-contract text, used by EVERY
    production prompt path (legacy/combined and narrowed) - never
    duplicated or hand-copied elsewhere. The vocabulary list is generated
    from the live `IdentifierType` enum (never hardcoded), so a new member
    added to that enum appears here automatically in both prompt paths."""
    lines = []
    for member in IdentifierType:
        description = _IDENTIFIER_TYPE_DESCRIPTIONS.get(
            member, "No guidance registered for this identifier type yet."
        )
        lines.append(f'- "{member.value}": {description}\n')
    lines.append(
        "- raw_value MUST contain the literal identifier value exactly as "
        "it appears in the chunk text - never a description, label, or "
        "paraphrase of it.\n"
    )
    lines.append(
        "- If there is no literal identifier value in the text, do not "
        "emit the identifier at all - omit the item instead of returning "
        "a partial object.\n"
    )
    lines.append(
        "- identifier_type MUST be exactly one of the values listed above. "
        "Never invent a new identifier_type label that is not in this "
        "list.\n"
    )
    lines.append(
        '- Never use placeholder/metadata labels such as "Document ID", '
        '"Chunk ID", "Section ID", or "Section Path" as an identifier '
        "value, unless that exact text is itself the real identifier "
        "printed in the chunk.\n"
    )
    lines.append(
        "- The chunk id, document id, and section path shown in this "
        "prompt's own metadata (the Chunk id / Section path lines below) "
        "describe where the text came from - they are prompt metadata for "
        "you to read, not document identifiers to extract.\n"
    )
    lines.append(
        "- source_chunk_id is provenance metadata for this response only - "
        "never emit a chunk id, document id, or any internal system id "
        "(e.g. chunk_*, doc_*) as an identifier's raw_value.\n"
    )
    lines.append(
        "- Do not emit menu names, chapter numbers, parameter labels, or "
        "display-message text as identifiers; omit them instead.\n"
    )
    lines.append(
        "- A manufacturer made the item; a supplier sold, distributed, or "
        "provided the item but did not necessarily make it. Use the "
        "manufacturers list for the former and the suppliers list for the "
        "latter. If a chunk does not distinguish the two roles, prefer "
        "manufacturers.\n"
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
