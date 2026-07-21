from __future__ import annotations

import re

from src.application.services.answer_generation.formatting.answer_format_policy import (
    AnswerFormatPolicy,
)

FORMAT_POLICY_VIOLATION_RULES_VERSION = "v1"

_NUMBERED_LIST_ITEM = re.compile(r"(?m)^\s*\d+[.)]\s+\S")
_BULLET_LIST_ITEM = re.compile(r"(?m)^\s*[-*•]\s+\S")
_TABLE_ROW = re.compile(r"(?m)^\s*\|.*\|\s*$")

_VIOLATION_DESCRIPTIONS = {
    "missing_numbered_steps": (
        'a numbered list of steps (e.g. "1. ...", "2. ...")'
    ),
    "missing_bullets": "bullet points",
    "missing_table": "a markdown table",
}


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


def build_format_policy_corrective_note(violations: list[str]) -> str:
    """Mirrors AnswerGenerationPromptExecutor's own schema-validation
    corrective-note pattern (`_build_corrective_note()`,
    execution/answer_generation_prompt_executor.py) -- same "explain
    exactly what was wrong, ask for a fix, nothing else" shape, applied to
    a structural format-policy miss instead of a JSON schema failure (W7b,
    answering_flow_weakness_remediation_plan.md)."""
    missing = "; ".join(
        _VIOLATION_DESCRIPTIONS.get(violation, violation) for violation in violations
    )
    return (
        "\n\nYour previous response did not follow the required format: "
        f"it is missing {missing}. Revise your answer to include this "
        "structure while keeping the same factual content."
    )
