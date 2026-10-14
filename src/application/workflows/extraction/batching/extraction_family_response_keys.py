from __future__ import annotations

from src.application.prompts.extraction import ExtractionPromptType

FAMILY_RESPONSE_KEY: dict[ExtractionPromptType, str] = {
    ExtractionPromptType.MAINTENANCE_TASK: "maintenance_tasks",
    ExtractionPromptType.SPARE_PART: "spare_parts",
    ExtractionPromptType.EQUIPMENT: "equipment",
    ExtractionPromptType.MANUFACTURER: "manufacturers",
    ExtractionPromptType.SUPPLIER: "suppliers",
    ExtractionPromptType.CONTACT_POINT: "contact_points",
    ExtractionPromptType.PROCEDURE: "procedures",
    ExtractionPromptType.SPECIFICATION: "specifications",
    ExtractionPromptType.SAFETY_WARNING: "safety_warnings",
    ExtractionPromptType.MAINTENANCE_INTERVAL: "maintenance_intervals",
    ExtractionPromptType.TROUBLESHOOTING: "troubleshooting_entries",
    ExtractionPromptType.IDENTIFIER: "identifiers",
}


def omitted_requested_family_keys(
    requested_types: frozenset[ExtractionPromptType] | None,
    response_text: str,
) -> tuple[str, ...]:
    """Purely observational: which requested family keys never appeared as
    a literal key in the raw response text at all, as opposed to appearing
    with an empty list - a real signal this schema's `default_factory=list`
    fields can't otherwise distinguish. Never used to raise or retry."""
    if requested_types is None:
        return ()
    return tuple(
        sorted(
            key
            for entity_type in requested_types
            if (key := FAMILY_RESPONSE_KEY.get(entity_type)) is not None
            and f'"{key}"' not in response_text
        )
    )
