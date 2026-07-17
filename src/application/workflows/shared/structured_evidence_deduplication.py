from __future__ import annotations


# Canonical identifier/structured-entity fingerprint dedup, previously
# reimplemented in both QuestionAnsweringWorkflow and
# StructuredEvidenceResolver. The two identifier-dedup copies were not
# byte-identical: StructuredEvidenceResolver assumes a real `Identifier`
# domain object and accesses its attributes directly (raising if one is
# missing), while QuestionAnsweringWorkflow defensively falls back with
# `getattr(...)`/`str(...)` coercion because it also dedupes identifiers
# coming straight off an inbound request payload. `strict=True` reproduces
# the former; the default reproduces the latter -- every call site keeps its
# exact previous behavior.
def deduplicate_identifiers(identifiers: list, *, strict: bool = False) -> list:
    deduplicated: list = []
    seen: set[tuple[str, str, str]] = set()
    for identifier in identifiers:
        if strict:
            fingerprint = (
                identifier.document_id,
                identifier.identifier_type.value,
                (identifier.normalized_value or identifier.raw_value).strip().lower(),
            )
        else:
            identifier_type = getattr(identifier, "identifier_type", None)
            fingerprint = (
                str(getattr(identifier, "document_id", "")),
                str(getattr(identifier_type, "value", identifier_type or "")),
                str(
                    getattr(identifier, "normalized_value", None)
                    or getattr(identifier, "raw_value", "")
                )
                .strip()
                .lower(),
            )
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        deduplicated.append(identifier)
    return deduplicated


def deduplicate_structured_entities(entities: list) -> list[dict]:
    deduplicated: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        fingerprint = (
            str(entity.get("_entity_type") or ""),
            str(_entity_identity_value(entity)),
        )
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        deduplicated.append(entity)
    return deduplicated


def _entity_identity_value(entity: dict) -> object:
    return (
        entity.get("source_chunk_id")
        or entity.get("manufacturer_id")
        or entity.get("supplier_id")
        or entity.get("contact_point_id")
        or entity.get("spare_part_id")
        or entity.get("equipment_id")
        or entity.get("task_id")
        or entity.get("procedure_id")
        or entity.get("specification_id")
        or entity.get("safety_warning_id")
        or entity.get("maintenance_interval_id")
        or entity.get("troubleshooting_id")
        or entity
    )
