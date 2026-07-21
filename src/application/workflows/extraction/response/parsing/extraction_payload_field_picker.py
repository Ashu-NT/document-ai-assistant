from __future__ import annotations

import re
from typing import Any

from src.application.workflows.extraction.extraction_text_value_normalizer import (
    normalize_extraction_text,
)

# `_pick`/`_optional_text`/`KEY_PATTERN` payload field access -- previously
# byte-identical copies in extraction_workflow.py and
# extraction_response_sanitizer.py. Consolidated here as the single shared
# primitive; both files keep thin wrapper methods delegating to these
# module-level functions since each is called from many places within its
# class.

KEY_PATTERN = re.compile(r"[^a-z0-9]+")


def pick_payload_value(payload: dict[str, Any], *keys: str) -> Any:
    normalized_payload = {
        KEY_PATTERN.sub("_", key.lower()).strip("_"): value
        for key, value in payload.items()
    }

    for key in keys:
        normalized_key = KEY_PATTERN.sub("_", key.lower()).strip("_")
        if normalized_key in normalized_payload:
            return normalized_payload[normalized_key]

    return None


def optional_payload_text(payload: dict[str, Any], *keys: str) -> str | None:
    value = pick_payload_value(payload, *keys)
    return normalize_extraction_text(value)
