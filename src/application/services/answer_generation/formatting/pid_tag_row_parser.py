from __future__ import annotations

import re

from src.application.services.answer_generation.formatting.spare_parts_row_fields import (
    has_identifying_content,
)

# Layout B: "V.00.01.01 <free text ...> <code>" -- a P&ID/tag style position
# code followed by unstructured descriptive text and an optional trailing
# part/order code.
_PID_ROW_PATTERN = re.compile(
    r"^(?P<pid>[A-Za-z]{1,4}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(?P<rest>.+)$"
)
_TRAILING_TOKEN_PATTERN = re.compile(r"(?P<token>[A-Za-z0-9./]{2,12})\s*$")
_PART_CODE_ALLOWED_PATTERN = re.compile(r"^[A-Za-z0-9]+(?:[./][A-Za-z0-9]+)*$")

# A small, generic vocabulary of common equipment-type nouns used only to
# split a free-text remainder into a "service" phrase and a "type" phrase --
# not tied to any particular document or manufacturer.
_TYPE_KEYWORDS = (
    "solenoid",
    "valve",
    "flange",
    "gauge",
    "sensor",
    "switch",
    "motor",
    "pump",
    "filter",
    "actuator",
    "transmitter",
    "regulator",
    "strainer",
    "coupling",
    "bracket",
    "gasket",
    "seal",
    "bearing",
    "fitting",
)


def row_from_pid_tag_line(text: str) -> dict[str, str] | None:
    match = _PID_ROW_PATTERN.match(text)
    if match is None:
        return None

    pid = match.group("pid")
    rest = match.group("rest").strip()
    row: dict[str, str] = {"pid_position": pid}

    remainder = rest
    token_match = _TRAILING_TOKEN_PATTERN.search(rest)
    if token_match is not None:
        candidate = token_match.group("token")
        if candidate.lower() != pid.lower() and _looks_like_part_code(candidate):
            remainder = rest[: token_match.start()].strip(" ,;:-")
            row["part_no"] = candidate

    leftover = _split_service_and_type(remainder, row)
    if leftover:
        row.setdefault("description", leftover)

    if not has_identifying_content(row):
        return None
    return row


def _split_service_and_type(text: str, row: dict[str, str]) -> str | None:
    if not text:
        return text
    lowered = text.lower()
    for keyword in _TYPE_KEYWORDS:
        idx = lowered.find(keyword)
        if idx == -1:
            continue
        if idx == 0:
            row["type"] = text.strip()
        else:
            service = text[:idx].strip(" ,;:-")
            if service:
                row["service"] = service
            row["type"] = text[idx:].strip(" ,;:-")
        return None
    return text


def _looks_like_part_code(token: str) -> bool:
    cleaned = token.strip().strip(".,;:")
    if not cleaned or not _PART_CODE_ALLOWED_PATTERN.match(cleaned):
        return False
    if not re.search(r"\d", cleaned):
        return False
    has_letter = bool(re.search(r"[A-Za-z]", cleaned))
    digit_count = len(re.findall(r"\d", cleaned))
    if has_letter:
        return digit_count >= 2
    return digit_count >= 4
