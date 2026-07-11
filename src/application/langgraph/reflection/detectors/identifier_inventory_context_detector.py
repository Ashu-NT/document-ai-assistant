from __future__ import annotations

from src.application.workflows.shared.identifier_value_pattern import (
    contains_identifier_value,
)

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
    if any(
        marker in normalized_answer
        for marker in (
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
    ):
        return contains_identifier_value(answer_text)
    return False
