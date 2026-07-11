from __future__ import annotations

from typing import Sequence

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.services.answer_generation.intent.answer_intent_vocabulary import (
    CHUNK_TYPE_TO_INTENT,
    STEP_PATTERN,
    TECHNICAL_VALUE_PATTERN,
)
from src.application.services.answer_generation.intent.question_signal_scorer import (
    looks_like_explicit_procedure_question,
    looks_like_maintenance_question,
    looks_like_specification_question,
    normalize_text,
)
from src.application.workflows.shared.identifier_value_pattern import (
    contains_identifier_value,
)
from src.domain.common import ChunkType
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _has_technical_values(content: str) -> bool:
    return bool(TECHNICAL_VALUE_PATTERN.search(content))


def _contains_procedure_steps(content: str) -> bool:
    normalized = content.lower()
    return bool(STEP_PATTERN.search(content)) or any(
        marker in normalized
        for marker in ("step 1", "step 2", "first,", "then ", "next ", "finally")
    )


def _contains_identifier_values(content: str) -> bool:
    normalized = content.lower()
    if any(
        marker in normalized
        for marker in (
            "serial number",
            "part number",
            "order code",
            "model number",
            "tag no",
            "drawing number",
        )
    ):
        return True
    return contains_identifier_value(content)


def _looks_like_table(content: str) -> bool:
    return sum(1 for line in content.splitlines() if "|" in line) >= 2


def _has_table_evidence(chunk: RetrievedChunk) -> bool:
    return (
        chunk.metadata.get("table_evidence_hydrated") == "true"
        or bool(chunk.metadata.get("table_rows_json"))
    )


def _looks_like_spare_parts_content(content: str) -> bool:
    normalized = content.lower()
    return "spare part" in normalized or "spare parts" in normalized


def apply_chunk_type_preference_signal(
    chunk_types: Sequence[ChunkType],
    scores: dict[AnswerIntent, int],
    matched: dict[AnswerIntent, list[str]],
) -> None:
    for chunk_type in chunk_types:
        answer_intent = CHUNK_TYPE_TO_INTENT.get(chunk_type)
        if answer_intent is None:
            continue
        scores[answer_intent] += 2
        matched[answer_intent].append(f"chunk_type:{chunk_type.value}")


def apply_chunk_content_signal(
    *,
    question: str,
    chunks: Sequence[RetrievedChunk],
    scores: dict[AnswerIntent, int],
    matched: dict[AnswerIntent, list[str]],
) -> None:
    if not chunks:
        return

    normalized_contents = [normalize_text(chunk.content) for chunk in chunks]
    allow_specification_boost = looks_like_specification_question(question) or not (
        looks_like_maintenance_question(question)
        and not looks_like_explicit_procedure_question(question)
    )
    if allow_specification_boost and any(
        _has_technical_values(chunk.content) for chunk in chunks
    ):
        scores[AnswerIntent.SPECIFICATION_SUMMARY] += 3
        matched[AnswerIntent.SPECIFICATION_SUMMARY].append(
            "context:technical_values"
        )
    if any(
        _looks_like_table(chunk.content) or _has_table_evidence(chunk)
        for chunk in chunks
    ):
        scores[AnswerIntent.TABLE_SUMMARY] += 2
        matched[AnswerIntent.TABLE_SUMMARY].append("context:table_like")
    if any(_looks_like_spare_parts_content(chunk.content) for chunk in chunks):
        scores[AnswerIntent.TABLE_SUMMARY] += 3
        matched[AnswerIntent.TABLE_SUMMARY].append("context:spare_parts_content")
    if any(_contains_identifier_values(chunk.content) for chunk in chunks):
        scores[AnswerIntent.IDENTIFIER_LOOKUP] += 2
        matched[AnswerIntent.IDENTIFIER_LOOKUP].append("context:identifier_values")
    if any(_contains_procedure_steps(chunk.content) for chunk in chunks):
        scores[AnswerIntent.PROCEDURE_STEPS] += 2
        matched[AnswerIntent.PROCEDURE_STEPS].append("context:ordered_steps")
    if any("maintenance" in content for content in normalized_contents):
        scores[AnswerIntent.MAINTENANCE_SUMMARY] += 2
        matched[AnswerIntent.MAINTENANCE_SUMMARY].append("context:maintenance_text")
    if any("warning" in content for content in normalized_contents):
        scores[AnswerIntent.SAFETY_WARNINGS] += 2
        matched[AnswerIntent.SAFETY_WARNINGS].append("context:safety_text")
    if any(
        any(term in content for term in ("fault", "cause", "remedy", "troubleshooting"))
        for content in normalized_contents
    ):
        scores[AnswerIntent.TROUBLESHOOTING] += 2
        matched[AnswerIntent.TROUBLESHOOTING].append(
            "context:troubleshooting_text"
        )
    if any(
        any(
            term in content
            for term in ("certificate", "approval", "inspection", "compliance")
        )
        for content in normalized_contents
    ):
        scores[AnswerIntent.CERTIFICATION_SUMMARY] += 2
        matched[AnswerIntent.CERTIFICATION_SUMMARY].append(
            "context:certification_text"
        )
