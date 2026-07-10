from __future__ import annotations

# Canonical maintenance free-text cleanup helpers, previously duplicated
# byte-identically between KeyValueExtractor and MaintenanceEntryMerger.
NOT_SPECIFIED = "Not specified"
MAINTENANCE_PLACEHOLDER_VALUES: frozenset[str] = frozenset(
    {"x", "-", "n/a", "na", "unknown"}
)


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    cleaned = cleaned.rstrip(" .;:")
    if not cleaned:
        return None
    if cleaned.lower() in MAINTENANCE_PLACEHOLDER_VALUES:
        return None
    return cleaned


def clean_interval(value: str | None) -> str:
    cleaned = clean_optional_text(value)
    if cleaned is None:
        return NOT_SPECIFIED
    return cleaned or NOT_SPECIFIED
