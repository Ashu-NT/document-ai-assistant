from __future__ import annotations

import re

from src.application.workflows.shared.identifier_value_pattern import (
    contains_identifier_value,
)

# How far past a label mention ("part number", "serial number", ...) to look
# for an identifier-shaped value. Bounds both a raw character count and a
# clause boundary (whichever is reached first) so a label and an unrelated
# identifier-shaped value that merely coexist somewhere in a long answer,
# possibly in a completely different sentence/clause, no longer coincidentally
# satisfy an identifier-inventory request.
_IDENTIFIER_VALUE_WINDOW_CHARS = 80
_CLAUSE_BOUNDARY_RE = re.compile(r"[.;\n]")

_IDENTIFIER_VALUE_LABEL_MARKERS = (
    "serial number",
    "serial numbers",
    "part number",
    "part numbers",
    "model number",
    "model numbers",
    "order code",
    "order number",
    "drawing number",
    "certificate number",
)


def _window_after_label(answer_text: str, label_end_index: int) -> str:
    remainder = answer_text[
        label_end_index : label_end_index + _IDENTIFIER_VALUE_WINDOW_CHARS
    ]
    boundary = _CLAUSE_BOUNDARY_RE.search(remainder)
    if boundary:
        return remainder[: boundary.start()]
    return remainder


def _identifier_value_near_any_label(answer_text: str, normalized_answer: str) -> bool:
    for marker in _IDENTIFIER_VALUE_LABEL_MARKERS:
        search_start = 0
        while True:
            index = normalized_answer.find(marker, search_start)
            if index == -1:
                break
            label_end_index = index + len(marker)
            window = _window_after_label(answer_text, label_end_index)
            if contains_identifier_value(window):
                return True
            search_start = label_end_index
    return False


_IDENTIFIER_LISTING_VERBS = (
    "list",
    "show",
    "display",
    "enumerate",
    "provide",
    "give me",
    "find all",
)
_IDENTIFIER_LISTING_MARKERS = (
    "part number",
    "part no",
    "serial number",
    "serial no",
    "order code",
    "order number",
    "model number",
    "drawing number",
    "document number",
    "tag number",
    "equipment id",
    "certificate",
    "manufacturer",
    "supplier",
)


def is_selected_document_identifier_inventory_context(
    *,
    question: str,
    answer_intent: str | None,
    selected_document_id: str | None,
    has_useful_evidence: bool,
) -> bool:
    if not selected_document_id or not has_useful_evidence:
        return False
    normalized_question = question.lower()
    normalized_intent = (answer_intent or "").lower()
    if "identifier" not in normalized_intent and not any(
        marker in normalized_question for marker in _IDENTIFIER_LISTING_MARKERS
    ):
        return False
    if not any(marker in normalized_question for marker in _IDENTIFIER_LISTING_VERBS):
        return False
    return any(marker in normalized_question for marker in _IDENTIFIER_LISTING_MARKERS)


def answer_contains_identifier_inventory(answer_text: str) -> bool:
    normalized_answer = answer_text.lower()
    if "requested identifiers" in normalized_answer:
        return True
    if any(
        label in normalized_answer
        for label in (
            "serial numbers:",
            "part numbers:",
            "model numbers:",
            "drawing numbers:",
            "certificate numbers:",
            "order / component codes:",
        )
    ):
        return True
    if any(marker in normalized_answer for marker in _IDENTIFIER_VALUE_LABEL_MARKERS):
        return _identifier_value_near_any_label(answer_text, normalized_answer)
    return False
