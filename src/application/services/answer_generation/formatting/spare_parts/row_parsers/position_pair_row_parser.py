from __future__ import annotations

import re

# Layout C: two "position description" pairs squeezed into one row, e.g. an
# exploded-view diagram rendered as a 2-column table where each cell holds
# its own position + short description ("14.00 Pump Casing").
_POSITION_PAIR_PATTERN = re.compile(
    r"(?P<pos>\d{1,3}\.\d{2})\s+(?P<desc>[A-Za-z][A-Za-z()/,\-]*(?:\s+[A-Za-z()/,\-]+)*)"
)


def rows_from_position_pairs(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for match in _POSITION_PAIR_PATTERN.finditer(text):
        description = match.group("desc").strip(" ,;:-")
        if not description:
            continue
        rows.append({"position": match.group("pos"), "description": description})
    return rows
