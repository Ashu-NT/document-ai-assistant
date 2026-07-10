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
#
# The `DN\s*\d+` alternative (e.g. "DN 50", a nominal-diameter pipe callout)
# was added to absorb two further LangGraph-side copies of this pattern
# (RetrievalSignalExtractor, DeterministicResearchPlanner) that had already
# drifted to include it independently. Folding it into the canonical pattern
# means the other four `contains_identifier_value` consumers now also match
# space-separated "DN 50"-style callouts they previously missed -- a small,
# deliberate behavior extension called for explicitly by the refactor plan
# (item 15), not an accidental side effect.
IDENTIFIER_VALUE_PATTERN = re.compile(
    r"\b([A-Z]{1,5}\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+|DN\s*\d+)\b",
    re.IGNORECASE,
)


def contains_identifier_value(text: str | None) -> bool:
    return bool(IDENTIFIER_VALUE_PATTERN.search(text or ""))


def extract_identifier_value(text: str) -> str | None:
    """Return the first identifier-shaped value in `text`, uppercased with
    internal whitespace removed (e.g. "dn 50" -> "DN50").

    Mirrors the historical behavior of
    DeterministicResearchPlanner._extract_identifier_value.
    """
    match = IDENTIFIER_VALUE_PATTERN.search(text.upper())
    return match.group(0).replace(" ", "") if match else None
