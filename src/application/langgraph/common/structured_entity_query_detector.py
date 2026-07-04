_STRUCTURED_DETAIL_TERMS = (
    "website",
    "url",
    "country",
    "based in",
    "located",
    "quantity",
    "how many",
    "in stock",
    "interval",
    "how often",
)
_STRUCTURED_ENTITY_TERMS: tuple[tuple[str, str], ...] = (
    ("manufacturer", "manufacturer"),
    ("supplier", "supplier"),
    ("vendor", "supplier"),
    ("distributor", "supplier"),
    ("spare part", "spare_part"),
    ("equipment", "equipment"),
    ("maintenance task", "maintenance_task"),
)


def detect_structured_entity_type(normalized_input: str) -> str | None:
    """Detects when a question is asking for a structured-entity detail
    field (e.g. a manufacturer's website, a spare part's quantity) rather
    than just the bare identifying value. Shared between DeterministicPlanner
    and the direct-answer graph nodes so both routes use identical
    detection logic."""
    normalized = normalized_input.lower()
    if not any(term in normalized for term in _STRUCTURED_DETAIL_TERMS):
        return None
    for term, entity_type in _STRUCTURED_ENTITY_TERMS:
        if term in normalized:
            return entity_type
    return None
