from __future__ import annotations

import re

from src.application.services.answer_generation.formatting.answer_format_policy import (
    AnswerFormatPolicy,
)

FORMAT_POLICY_VIOLATION_RULES_VERSION = "v1"

_NUMBERED_LIST_ITEM = re.compile(r"(?m)^\s*\d+[.)]\s+\S")
_BULLET_LIST_ITEM = re.compile(r"(?m)^\s*[-*•]\s+\S")
_TABLE_ROW = re.compile(r"(?m)^\s*\|.*\|\s*$")


def detect_format_policy_violations(
    *, format_policy: AnswerFormatPolicy | None, answer_text: str
) -> list[str]:
    if format_policy is None or not answer_text:
        return []
    violations: list[str] = []
    if format_policy.include_steps and not _NUMBERED_LIST_ITEM.search(answer_text):
        violations.append("missing_numbered_steps")
    if format_policy.include_bullets and not _BULLET_LIST_ITEM.search(answer_text):
        violations.append("missing_bullets")
    if format_policy.include_table and not _TABLE_ROW.search(answer_text):
        violations.append("missing_table")
    return violations
