from __future__ import annotations

import json

from src.application.workflows.retrieval import RetrievalQueryIntent
from src.application.workflows.retrieval.intent.retrieval_query_intent_markers import (
    IDENTIFIER_TABLE_MARKERS,
    SPECIFICATION_TABLE_MARKERS,
    TABLE_REQUEST_MARKERS,
)
from src.application.workflows.retrieval.table_focus import is_table_focused_query
from src.application.workflows.shared.maintenance_signal_detection import (
    MAINTENANCE_INTERVAL_MARKERS,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery, RetrievedChunk
from src.infrastructure.retrieval.rerankers.deterministic.reranker_metadata_extractors import (
    metadata_float,
)


def table_query_evidence_score(
    *,
    intent: RetrievalQueryIntent,
    query: RetrievalQuery,
    query_text: str,
    chunk: RetrievedChunk,
    role: str,
) -> float:
    if not is_table_focused_query(query=query, intent=intent):
        return 0.0

    has_direct_table_evidence = _has_direct_table_evidence(chunk)
    table_confidence = min(
        metadata_float(chunk, "table_category_confidence") * 4.0,
        4.0,
    )
    score = 0.0

    if has_direct_table_evidence:
        score += 10.0
        score += table_confidence
        if role == "atomic_evidence":
            score += 4.0
        if chunk.chunk_type == ChunkType.SPARE_PARTS_TABLE:
            score += 5.0
        elif chunk.chunk_type in {
            ChunkType.TECHNICAL_SPECIFICATION,
            ChunkType.CERTIFICATION_INFO,
            ChunkType.MAINTENANCE_INTERVAL,
            ChunkType.TROUBLESHOOTING,
        }:
            score += 3.0
    else:
        score -= _companion_penalty(role, chunk.chunk_type)

    if _has_any_marker(query_text, TABLE_REQUEST_MARKERS):
        score += 4.0 if has_direct_table_evidence else -4.0

    if (
        intent == RetrievalQueryIntent.MAINTENANCE
        and _has_any_marker(query_text, MAINTENANCE_INTERVAL_MARKERS)
        and chunk.chunk_type == ChunkType.MAINTENANCE_INTERVAL
        and has_direct_table_evidence
    ):
        score += 4.0

    if (
        intent == RetrievalQueryIntent.SPECIFICATION
        and _has_any_marker(query_text, SPECIFICATION_TABLE_MARKERS)
        and chunk.chunk_type
        in {ChunkType.TECHNICAL_SPECIFICATION, ChunkType.CERTIFICATION_INFO}
        and has_direct_table_evidence
    ):
        score += 4.0

    if (
        intent == RetrievalQueryIntent.IDENTIFIER
        and _has_any_marker(query_text, IDENTIFIER_TABLE_MARKERS)
        and has_direct_table_evidence
    ):
        score += 4.0

    return score
def _has_direct_table_evidence(chunk: RetrievedChunk) -> bool:
    if chunk.chunk_type == ChunkType.SPARE_PARTS_TABLE:
        return True
    if chunk.metadata.get("logical_table_family_id"):
        return True
    if chunk.metadata.get("table_category"):
        return True
    if chunk.metadata.get("table_row_start") or chunk.metadata.get("table_row_end"):
        return True
    if _has_table_ids(chunk):
        return True
    return "|" in chunk.content


def _has_table_ids(chunk: RetrievedChunk) -> bool:
    raw_value = chunk.metadata.get("hydrated_table_ids") or chunk.metadata.get("table_ids")
    if not raw_value:
        return False
    if raw_value.startswith("["):
        try:
            decoded = json.loads(raw_value)
        except ValueError:
            return False
        return isinstance(decoded, list) and any(str(value).strip() for value in decoded)
    return any(part.strip() for part in raw_value.split(","))


def _companion_penalty(role: str, chunk_type: ChunkType) -> float:
    if role == "overview_companion":
        return 14.0
    if role == "context_companion":
        return 10.0
    if role == "asset_companion":
        return 9.0
    if chunk_type == ChunkType.OVERVIEW:
        return 8.0
    if chunk_type == ChunkType.GENERAL:
        return 4.0
    return 0.0


def _has_any_marker(query_text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in query_text for marker in markers)
