from __future__ import annotations

import re

from src.application.workflows.shared.maintenance_action_verbs import (
    MAINTENANCE_ACTION_VERBS,
)

_MAINTENANCE_ACTION_PATTERN = re.compile(
    r"\b(" + "|".join(MAINTENANCE_ACTION_VERBS) + r")\b",
    re.IGNORECASE,
)
_SCHEDULE_PREFIX_TOKENS = frozenset({"a", "d", "m", "q", "s", "sa", "w", "y"})
_SCHEDULE_PREFIX_WITH_DELIMITER_PATTERN = re.compile(
    r"^(?P<prefix>(?:[A-Za-z]{1,2}\s*){2,8})\s*[:=\-]+\s*(?P<rest>.+)$"
)
_SCHEDULE_PREFIX_WITH_SPACE_PATTERN = re.compile(
    r"^(?P<prefix>(?:[A-Za-z]{1,2}\s+){2,8})(?P<rest>.+)$"
)
_SCHEDULE_PREFIX_TOKEN_PATTERN = re.compile(r"[A-Za-z]{1,2}")


def clean_task(task: str | None) -> str | None:
    if task is None:
        return None
    cleaned = " ".join(task.strip().split())
    cleaned = _strip_leading_schedule_prefix(cleaned)
    if ":" in cleaned:
        prefix, suffix = cleaned.split(":", 1)
        if _MAINTENANCE_ACTION_PATTERN.search(suffix):
            cleaned = suffix.strip()
    return cleaned.rstrip(" .;:") or None


def _strip_leading_schedule_prefix(value: str) -> str:
    for pattern in (
        _SCHEDULE_PREFIX_WITH_DELIMITER_PATTERN,
        _SCHEDULE_PREFIX_WITH_SPACE_PATTERN,
    ):
        match = pattern.match(value)
        if match is None:
            continue
        prefix_tokens = [
            token.lower()
            for token in _SCHEDULE_PREFIX_TOKEN_PATTERN.findall(match.group("prefix"))
        ]
        rest = match.group("rest").strip()
        if (
            prefix_tokens
            and all(token in _SCHEDULE_PREFIX_TOKENS for token in prefix_tokens)
            and _MAINTENANCE_ACTION_PATTERN.search(rest)
        ):
            return rest
    return value
