from __future__ import annotations

import re

from src.application.workflows.shared.maintenance_action_verbs import (
    MAINTENANCE_ACTION_VERBS,
)

_MAINTENANCE_ACTION_PATTERN = re.compile(
    r"\b(" + "|".join(MAINTENANCE_ACTION_VERBS) + r")\b",
    re.IGNORECASE,
)


def clean_task(task: str | None) -> str | None:
    if task is None:
        return None
    cleaned = " ".join(task.strip().split())
    if ":" in cleaned:
        prefix, suffix = cleaned.split(":", 1)
        if _MAINTENANCE_ACTION_PATTERN.search(suffix):
            cleaned = suffix.strip()
    return cleaned.rstrip(" .;:") or None
