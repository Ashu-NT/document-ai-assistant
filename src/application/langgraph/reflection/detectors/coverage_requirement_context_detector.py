from __future__ import annotations

import re

_COMPLETENESS_CLAIM_PHRASES = (
    "here is the complete list",
    "here are all",
    "the complete list",
    "a complete list",
    "full list",
    "all of the following",
    "this is a complete",
    "lists all",
    "includes all",
)

# Pragmatic v1 heuristic (mirrors QuestionClauseSplitter's own philosophy):
# matches "Step N" mentions anywhere, or a line that opens with "N." / "N)"
# -- not full NLP, and deliberately errs toward under-detecting a gap
# (missing a genuinely irregular numbering style) rather than flagging a
# well-formed procedure as broken.
_STEP_PATTERN = re.compile(r"step\s+(\d+)\b", re.IGNORECASE)
_NUMBERED_LINE_PATTERN = re.compile(r"^\s*(\d+)[.)]\s", re.MULTILINE)


def claims_completeness(answer_text: str | None) -> bool:
    normalized = " ".join((answer_text or "").lower().split())
    return any(phrase in normalized for phrase in _COMPLETENESS_CLAIM_PHRASES)


def has_step_sequence_gap(answer_text: str | None) -> bool:
    text = answer_text or ""
    numbers = [int(match.group(1)) for match in _STEP_PATTERN.finditer(text)]
    if len(numbers) < 2:
        numbers = [int(match.group(1)) for match in _NUMBERED_LINE_PATTERN.finditer(text)]
    if len(numbers) < 2:
        return False
    return any(
        current - previous > 1 for previous, current in zip(numbers, numbers[1:])
    )
