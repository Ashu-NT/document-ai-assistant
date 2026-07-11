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
_IDENTIFYING_ROW_LABELS = (
    "description:",
    "type:",
    "part no.:",
    "p&id position:",
    "service:",
    "raw row:",
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
    has_raw_row = "raw row:" in normalized
    has_partial_notice = "partial" in normalized
    return has_identifying_row or has_raw_row or has_partial_notice


def answer_only_has_unit_artifact_rows(answer_text: str) -> bool:
    normalized = answer_text.lower()
    if not _UNIT_ARTIFACT_ROW_PATTERN.search(normalized):
        return False
    return not any(label in normalized for label in _IDENTIFYING_ROW_LABELS)


def answer_denies_spare_parts_list(answer_text: str) -> bool:
    normalized = " ".join(answer_text.lower().split())
    if any(phrase in normalized for phrase in _SPARE_PARTS_DENIAL_PHRASES):
        return True
    return "spare part" in normalized and (
        "was not found" in normalized or "not found" in normalized
    )
