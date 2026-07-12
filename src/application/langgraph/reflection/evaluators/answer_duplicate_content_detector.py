from __future__ import annotations

from dataclasses import dataclass
import re

_BULLET_PREFIX_RE = re.compile(r"^\s*(?:[-*•]|\d+[\).\s])+")
_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True, slots=True)
class DuplicateContentAnalysis:
    duplicate_line_count: int

    @property
    def has_duplicate_content(self) -> bool:
        return self.duplicate_line_count > 0


def analyze_duplicate_content(answer_text: str) -> DuplicateContentAnalysis:
    seen: set[str] = set()
    duplicate_count = 0
    for line in (answer_text or "").splitlines():
        normalized = _normalize_line(line)
        if normalized is None:
            continue
        if normalized in seen:
            duplicate_count += 1
            continue
        seen.add(normalized)
    return DuplicateContentAnalysis(duplicate_line_count=duplicate_count)


def _normalize_line(line: str) -> str | None:
    stripped = _BULLET_PREFIX_RE.sub("", line.strip())
    stripped = _WHITESPACE_RE.sub(" ", stripped).strip(" -:|")
    if len(stripped) < 20:
        return None
    if not any(char.isalpha() for char in stripped):
        return None
    return stripped.lower()
