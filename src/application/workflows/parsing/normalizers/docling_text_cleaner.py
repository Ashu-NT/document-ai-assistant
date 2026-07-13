from __future__ import annotations

_MOJIBAKE_MARKERS = (
    "\u00c3\u00a2\u20ac",
    "\u00c3\u00a2\u20ac\u00e2\u201e\u00a2",
    "\u00c3\u00a2\u20ac\u00c5\u201c",
    "\u00c3\u00a2\u20ac\u00c2\u009d",
    "\u00c3\u00a2\u20ac\u00e2\u20ac\u0153",
    "\u00c3\u00a2\u20ac\u00e2\u20ac\u009d",
    "\u00c3\u00a2\u20ac\u00c2\u00a6",
    "\u00c3\u0192",
    "\u00c3\u201a",
    "\u00e2\u20ac\u2122",
    "\u00e2\u20ac\u0153",
    "\u00e2\u20ac\u009d",
    "\u00e2\u20ac\u201c",
    "\u00e2\u20ac\u201d",
    "\u00e2\u20ac\u00a6",
)
_DIRECT_REPLACEMENTS = {
    "\u00e2\u20ac\u2122": "\u2019",
    "\u00e2\u20ac\u0153": "\u201c",
    "\u00e2\u20ac\u009d": "\u201d",
    "\u00e2\u20ac\u201c": "\u2013",
    "\u00e2\u20ac\u201d": "\u2014",
    "\u00e2\u20ac\u00a6": "\u2026",
    "\u00c2\u00a0": " ",
}


def repair_docling_text(value: str | None) -> str:
    text = str(value or "")
    if not text:
        return ""

    normalized = text.replace("\xa0", " ")
    repaired = _repair_utf8_mojibake(normalized)
    repaired = _apply_direct_replacements(repaired)
    return repaired.strip()


def _repair_utf8_mojibake(value: str) -> str:
    candidate = value
    for _ in range(2):
        if not _looks_like_mojibake(candidate):
            break
        repaired = _best_roundtrip_candidate(candidate)
        if repaired is None:
            break
        if _mojibake_score(repaired) >= _mojibake_score(candidate):
            break
        candidate = repaired
    return candidate


def _best_roundtrip_candidate(value: str) -> str | None:
    candidates = [
        repaired
        for repaired in (
            _try_cp1252_utf8_roundtrip(value),
            _try_latin1_utf8_roundtrip(value),
        )
        if repaired is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=_mojibake_score)


def _try_cp1252_utf8_roundtrip(value: str) -> str | None:
    try:
        return value.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None


def _try_latin1_utf8_roundtrip(value: str) -> str | None:
    try:
        return value.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None


def _looks_like_mojibake(value: str) -> bool:
    return any(marker in value for marker in _MOJIBAKE_MARKERS) or any(
        0x80 <= ord(character) <= 0x9F
        for character in value
    )


def _mojibake_score(value: str) -> int:
    marker_score = sum(value.count(marker) for marker in _MOJIBAKE_MARKERS)
    control_score = sum(
        1
        for character in value
        if 0x80 <= ord(character) <= 0x9F
    )
    return marker_score + control_score


def _apply_direct_replacements(value: str) -> str:
    repaired = value
    for source, target in _DIRECT_REPLACEMENTS.items():
        repaired = repaired.replace(source, target)
    return repaired
