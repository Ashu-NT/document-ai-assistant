from __future__ import annotations

import sys


def preview_text(
    value: object,
    limit: int = 180,
    *,
    rstrip: bool = False,
    empty_fallback: str | None = None,
) -> str:
    """Normalizes whitespace and truncates to `limit` characters, appending
    "...". `rstrip`/`empty_fallback` cover the small cosmetic variations
    this had drifted into across call sites before consolidation (some
    trimmed trailing whitespace right before the ellipsis, one returned a
    "-" placeholder for an empty value instead of "")."""
    text = " ".join(str(value or "").split())
    if not text and empty_fallback is not None:
        return empty_fallback
    if len(text) <= limit:
        return text
    truncated = text[: max(0, limit - 3)]
    if rstrip:
        truncated = truncated.rstrip()
    return f"{truncated}..."


def console_safe_text(value: str | None) -> str:
    """Re-encodes text so it can't crash console output on a terminal whose
    encoding can't represent every character, falling back to UTF-8 if the
    terminal's own reported encoding is itself invalid."""
    if value is None:
        return ""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return value.encode(encoding, errors="replace").decode(encoding, errors="replace")
    except LookupError:
        return value.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
