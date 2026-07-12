from __future__ import annotations

import sys

# How far back from the cut point to look for a whitespace boundary before
# giving up and falling back to a raw slice (finding 6.10) -- bounded so a
# single long unbroken token (e.g. a URL or identifier) can't force an
# unbounded backward scan.
_WORD_BOUNDARY_LOOKBACK_CHARS = 40
_WHITESPACE_CHARS = (" ", "\t", "\n", "\r")


def truncate_at_word_boundary(text: str, limit: int) -> str:
    """Slices `text` to at most `limit` characters, preferring to stop at
    the last whitespace boundary within a short lookback window so a
    truncation doesn't cut a word in half. Falls back to a raw character
    slice if no whitespace boundary exists within that window (e.g. one
    long unbroken token) rather than scanning the whole string."""
    if limit <= 0:
        return ""
    if limit >= len(text):
        return text
    truncated = text[:limit]
    if text[limit] in _WHITESPACE_CHARS:
        # The cut already lands exactly at a word boundary.
        return truncated
    lookback_start = max(0, limit - _WORD_BOUNDARY_LOOKBACK_CHARS)
    boundary = max(
        truncated.rfind(char, lookback_start) for char in _WHITESPACE_CHARS
    )
    if boundary == -1:
        return truncated
    return truncated[:boundary]


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
    truncated = truncate_at_word_boundary(text, max(0, limit - 3))
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
