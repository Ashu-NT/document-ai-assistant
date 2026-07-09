from __future__ import annotations

import re

# Generic "does this text contain something shaped like a part/serial/order/
# drawing number" detector -- previously duplicated three ways with a subtle
# drift already baked in: structured_identifier_query_analyzer.py and
# reflection_validator.py both compiled this case-insensitively, but
# answer_intent_analyzer.py's copy omitted re.IGNORECASE (so it silently
# missed lowercase-written identifier values that the other two would have
# caught). Consolidated here as the case-insensitive version, matching the
# majority behavior.
IDENTIFIER_VALUE_PATTERN = re.compile(
    r"\b([A-Z]{1,5}\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+)\b",
    re.IGNORECASE,
)


def contains_identifier_value(text: str | None) -> bool:
    return bool(IDENTIFIER_VALUE_PATTERN.search(text or ""))
