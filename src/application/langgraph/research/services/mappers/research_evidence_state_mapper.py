from __future__ import annotations

from typing import Any

from src.application.langgraph.research.models import ResearchEvidence
from src.application.langgraph.research.services.mappers.state_mapping_primitives import (
    float_or_none,
    int_or_none,
    str_or_none,
)


def evidence_from_list(value: Any) -> list[ResearchEvidence]:
    if not isinstance(value, list):
        return []
    evidence: list[ResearchEvidence] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        evidence.append(
            ResearchEvidence(
                evidence_id=str(item.get("evidence_id") or ""),
                task_id=str(item.get("task_id") or ""),
                chunk_id=str(item.get("chunk_id") or ""),
                document_id=str(item.get("document_id") or ""),
                document_title=str_or_none(item.get("document_title")),
                section_path=[
                    str(section)
                    for section in list(item.get("section_path") or [])
                    if str(section).strip()
                ],
                page_start=int_or_none(item.get("page_start")),
                page_end=int_or_none(item.get("page_end")),
                chunk_type=str_or_none(item.get("chunk_type")),
                score=float_or_none(item.get("score")),
                content_excerpt=str(item.get("content_excerpt") or ""),
                source_tool=str(item.get("source_tool") or ""),
                diagnostics=dict(item.get("diagnostics") or {}),
            )
        )
    return evidence
