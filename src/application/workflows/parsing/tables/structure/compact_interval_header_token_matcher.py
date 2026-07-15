import re


class CompactIntervalHeaderTokenMatcher:
    """Recognizes a single token as a maintenance-schedule interval code
    (bare letter or full word, e.g. "d"/"daily"). Isolated from the generic
    Docling row-grid builder so schedule vocabulary lives in the
    shape-detection layer, not the generic parsing normalizer."""

    _PATTERN = re.compile(
        r"^(?:d|w|m|q|s|a|daily|weekly|monthly|quarterly|semi-annual|semi annual|annual|annually|yearly)$",
        re.IGNORECASE,
    )

    def matches(self, value: str) -> bool:
        return bool(self._PATTERN.match(value.strip()))
