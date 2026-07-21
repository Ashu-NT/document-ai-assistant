from __future__ import annotations

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)

TABLE_EVIDENCE_PHRASE = "spare parts list"
TABLE_HEADER_EVIDENCE_MARKERS = (
    "position no",
    "pos.",
    "qty",
    "denomination",
    "designation",
    "part no",
    "spare part no",
    "article no",
    "order no",
    "material no",
    "p&id",
    "tag",
    "service function",
    "exploded views",
)


def has_table_evidence(source: AnswerSource) -> bool:
    section_title = (source.chunk_name or "Spare Parts List").lower()
    if TABLE_EVIDENCE_PHRASE in section_title:
        return True
    content_lower = source.content.lower()
    if TABLE_EVIDENCE_PHRASE in content_lower:
        return True
    return any(marker in content_lower for marker in TABLE_HEADER_EVIDENCE_MARKERS)
