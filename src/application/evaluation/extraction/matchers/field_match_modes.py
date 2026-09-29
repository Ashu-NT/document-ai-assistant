"""Per-(entity_type, field) match mode configuration.

Production dedup (`normalize_for_dedup_key`) always does exact normalized
equality - appropriate when comparing two LLM outputs of the same document,
which tend to reproduce near-identical wording. A human annotator writing
golden `expected_fields`, however, will often paraphrase or excerpt long
prose (a safety message, a troubleshooting symptom/cause/remedy, a
procedure step) rather than transcribe it verbatim. For exactly those
long-prose fields we allow a documented CONTAINS fallback (normalized
expected text must appear as a substring of the normalized actual text)
after an exact match fails - every other field always requires exact
normalized equality, matching production identity semantics precisely.
"""

from enum import StrEnum

from src.application.evaluation.extraction.extraction_entity_type import (
    ExtractionEntityType,
)


class FieldMatchMode(StrEnum):
    EXACT = "exact"
    CONTAINS = "contains"


_CONTAINS_ELIGIBLE_FIELDS: dict[ExtractionEntityType, frozenset[str]] = {
    ExtractionEntityType.MAINTENANCE_TASK: frozenset({"title", "description"}),
    ExtractionEntityType.SPARE_PART: frozenset({"description"}),
    ExtractionEntityType.EQUIPMENT_INFO: frozenset(),
    ExtractionEntityType.MANUFACTURER: frozenset(),
    ExtractionEntityType.SUPPLIER: frozenset(),
    ExtractionEntityType.CONTACT_POINT: frozenset(),
    ExtractionEntityType.PROCEDURE: frozenset({"title", "steps"}),
    ExtractionEntityType.SPECIFICATION: frozenset(),
    ExtractionEntityType.SAFETY_WARNING: frozenset({"message"}),
    ExtractionEntityType.MAINTENANCE_INTERVAL: frozenset(),
    ExtractionEntityType.TROUBLESHOOTING_ENTRY: frozenset(
        {"symptom", "cause", "remedy"}
    ),
    ExtractionEntityType.EXTRACTED_IDENTIFIER: frozenset(),
}


def match_mode_for_field(
    entity_type: ExtractionEntityType, field_name: str
) -> FieldMatchMode:
    if field_name in _CONTAINS_ELIGIBLE_FIELDS.get(entity_type, frozenset()):
        return FieldMatchMode.CONTAINS
    return FieldMatchMode.EXACT


__all__ = ["FieldMatchMode", "match_mode_for_field"]
