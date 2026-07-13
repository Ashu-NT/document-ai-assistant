import re


class IntervalExpressionParser:
    _CALENDAR_MARKERS = (
        "daily",
        "day",
        "days",
        "weekly",
        "week",
        "weeks",
        "monthly",
        "month",
        "months",
        "quarterly",
        "annual",
        "annually",
        "yearly",
        "year",
        "years",
    )
    _EVENT_MARKERS = (
        "before startup",
        "before start-up",
        "after startup",
        "after start-up",
        "after shutdown",
        "before operation",
        "after cleaning",
    )

    def is_interval_expression(self, value: str) -> bool:
        text = value.casefold().strip()
        if not text:
            return False

        if any(marker in text for marker in self._CALENDAR_MARKERS):
            return True
        if any(marker in text for marker in self._EVENT_MARKERS):
            return True
        return bool(
            re.search(
                r"\b\d+(?:\.\d+)?\s*(?:h|hr|hrs|hour|hours|day|days|week|weeks|month|months|year|years)\b",
                text,
            )
        )
