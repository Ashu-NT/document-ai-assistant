from __future__ import annotations

from pydantic import ValidationError


def is_json_validation_error(exc: ValidationError) -> bool:
    """True if a pydantic ValidationError stems from malformed JSON (the LLM
    response wasn't parseable JSON at all) rather than a schema mismatch."""
    return any(error.get("type") == "json_invalid" for error in exc.errors())


def strip_code_fences_if_opened(payload: str) -> str:
    """Strips a leading/trailing markdown code fence when the payload opens
    with one, regardless of whether a closing fence is present."""
    stripped = (payload or "").strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 2:
            stripped = "\n".join(lines[1:-1]).strip()
    return stripped


def strip_code_fences_if_wrapped(payload: str) -> str:
    """Strips a markdown code fence only when the payload both opens and
    closes with one -- stricter than strip_code_fences_if_opened()."""
    stripped = (payload or "").strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 2:
            return "\n".join(lines[1:-1]).strip()
    return stripped
