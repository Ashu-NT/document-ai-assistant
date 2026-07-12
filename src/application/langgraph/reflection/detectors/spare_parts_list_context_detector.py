from __future__ import annotations

import re

_SPARE_PARTS_LIST_QUESTION_MARKERS = ("spare part", "spare parts")
_SPARE_PARTS_DENIAL_PHRASES = (
    "no spare part list",
    "no spare parts list",
    "no spare part table",
    "no spare parts table",
    "no specific spare part",
    "no specific spare parts",
    "spare part list table was not found",
    "spare parts list table was not found",
    "no comprehensive table of spare parts",
    "no comprehensive spare parts table",
    "no table or list of spare parts",
    "not found directly related to the question",
)
_UNIT_ARTIFACT_ROW_PATTERN = re.compile(
    r"quantity:\s*(pce|pcs|pc|ea|each|unit|units)\b",
    re.IGNORECASE,
)
_UNIT_ARTIFACT_TABLE_PATTERN = re.compile(
    r"\|\s*(pce|pcs|pc|ea|each|unit|units)\s*\|",
    re.IGNORECASE,
)
_QUANTITY_ONLY_TABLE_HEADER_PATTERN = re.compile(
    r"\|\s*quantity\s*\|",
    re.IGNORECASE,
)
_IDENTIFYING_ROW_LABELS = (
    "description:",
    "type:",
    "part no.:",
    "p&id position:",
    "service:",
    "raw row:",
)
_IDENTIFYING_TABLE_HEADERS = (
    "description",
    "type",
    "part no.",
    "p&id position",
    "service",
)


def is_selected_document_spare_parts_list_context(
    *,
    question: str,
    has_relevant_spare_parts_evidence: bool,
) -> bool:
    if not has_relevant_spare_parts_evidence:
        return False
    normalized_question = question.lower()
    return any(
        marker in normalized_question
        for marker in _SPARE_PARTS_LIST_QUESTION_MARKERS
    )


def is_legitimate_partial_spare_parts_answer(answer_text: str) -> bool:
    normalized = " ".join(answer_text.lower().split())
    if not any(marker in normalized for marker in _SPARE_PARTS_LIST_QUESTION_MARKERS):
        return False
    if answer_denies_spare_parts_list(answer_text):
        return False
    if answer_only_has_unit_artifact_rows(answer_text):
        return False
    if not re.search(r"\bpages?\b", normalized):
        return False
    has_identifying_row = any(label in normalized for label in _IDENTIFYING_ROW_LABELS)
    has_identifying_table = (
        "+" in answer_text
        and "|" in answer_text
        and any(label in normalized for label in _IDENTIFYING_TABLE_HEADERS)
    )
    has_raw_row = "raw row:" in normalized
    # A bare "partial" notice with no actual row data is not enough on its
    # own -- an answer claiming "this is only a partial list (see page 4)"
    # with zero identifying/raw rows must not be accepted as legitimate
    # partial coverage. Require at least one real data signal.
    return has_identifying_row or has_identifying_table or has_raw_row


def answer_only_has_unit_artifact_rows(answer_text: str) -> bool:
    normalized = answer_text.lower()
    has_artifact_row = _UNIT_ARTIFACT_ROW_PATTERN.search(normalized) is not None
    has_artifact_table = (
        _QUANTITY_ONLY_TABLE_HEADER_PATTERN.search(answer_text) is not None
        and _UNIT_ARTIFACT_TABLE_PATTERN.search(answer_text) is not None
    )
    if not has_artifact_row and not has_artifact_table:
        return False
    return not any(label in normalized for label in _IDENTIFYING_ROW_LABELS) and not (
        "+" in answer_text
        and "|" in answer_text
        and any(label in normalized for label in _IDENTIFYING_TABLE_HEADERS)
    )


def answer_denies_spare_parts_list(answer_text: str) -> bool:
    normalized = " ".join(answer_text.lower().split())
    if any(phrase in normalized for phrase in _SPARE_PARTS_DENIAL_PHRASES):
        return True
    return "spare part" in normalized and (
        "was not found" in normalized or "not found" in normalized
    )
