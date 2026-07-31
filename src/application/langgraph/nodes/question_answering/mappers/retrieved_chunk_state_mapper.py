from __future__ import annotations

from typing import Any

from src.domain.common import BoundingBox, ChunkType, SourceLocation
from src.domain.document.value_objects import ChunkStatistics
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk
from src.domain.retrieval.row_bounding_box import RowBoundingBox


def dict_to_chunk(payload: dict[str, Any]) -> RetrievedChunk:
    citation_payload = payload.get("citation")
    citation = dict_to_citation(citation_payload) if isinstance(citation_payload, dict) else None
    return RetrievedChunk(
        chunk_id=str(payload.get("chunk_id") or ""),
        document_id=str(payload.get("document_id") or ""),
        content=str(payload.get("content") or ""),
        score=float(payload.get("score") or 0.0),
        retrieval_source=str(payload.get("retrieval_source") or "merged"),
        chunk_type=chunk_type_from_value(payload.get("chunk_type")),
        section_id=str(payload.get("section_id") or "") or None,
        section_path=[
            str(part) for part in (payload.get("section_path") or []) if str(part)
        ],
        source=dict_to_source(payload.get("source")),
        citation=citation,
        statistics=dict_to_statistics(payload.get("statistics")),
        metadata={
            str(key): str(value)
            for key, value in (payload.get("metadata") or {}).items()
        }
        if isinstance(payload.get("metadata"), dict)
        else {},
        identifier_values=[
            str(value)
            for value in (payload.get("identifier_values") or [])
            if str(value)
        ]
        if isinstance(payload.get("identifier_values"), list)
        else [],
    )


def dict_to_source(payload: Any) -> SourceLocation:
    if not isinstance(payload, dict):
        return SourceLocation()
    page_start = payload.get("page_start")
    page_end = payload.get("page_end")
    return SourceLocation(
        page_start=int(page_start) if isinstance(page_start, int) else None,
        page_end=int(page_end) if isinstance(page_end, int) else None,
        bbox=_bbox_from_payload(payload.get("bbox")),
    )


def dict_to_citation(payload: dict[str, Any]) -> Citation:
    source = dict_to_source(payload.get("source"))
    return Citation(
        citation_id=str(payload.get("citation_id") or ""),
        document_id=str(payload.get("document_id") or ""),
        chunk_id=str(payload.get("chunk_id") or "") or None,
        section_id=str(payload.get("section_id") or "") or None,
        document_name=str(payload.get("document_name") or "") or None,
        section_title=str(payload.get("section_title") or "") or None,
        source=source,
        row_bboxes=_row_bboxes_from_payload(payload.get("row_bboxes")),
    )


def _bbox_from_payload(value: Any) -> BoundingBox | None:
    if not isinstance(value, dict):
        return None
    try:
        return BoundingBox(
            x1=float(value["x1"]),
            y1=float(value["y1"]),
            x2=float(value["x2"]),
            y2=float(value["y2"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _row_bboxes_from_payload(value: Any) -> list[RowBoundingBox] | None:
    if not isinstance(value, list):
        return None
    row_bboxes: list[RowBoundingBox] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        bbox = _bbox_from_payload(item.get("bbox"))
        if bbox is None:
            continue
        row_index = item.get("row_index")
        if not isinstance(row_index, int):
            continue
        page_number = item.get("page_number")
        row_bboxes.append(
            RowBoundingBox(
                row_index=row_index,
                page_number=page_number if isinstance(page_number, int) else None,
                bbox=bbox,
            )
        )
    return row_bboxes or None


def dict_to_statistics(payload: Any) -> ChunkStatistics | None:
    if not isinstance(payload, dict):
        return None

    char_count = payload.get("char_count")
    token_count_estimate = payload.get("token_count_estimate")
    try:
        normalized_char_count = (
            int(char_count) if char_count is not None else None
        )
    except (TypeError, ValueError):
        normalized_char_count = None
    try:
        normalized_token_count = (
            int(token_count_estimate) if token_count_estimate is not None else None
        )
    except (TypeError, ValueError):
        normalized_token_count = None

    if normalized_char_count is None and normalized_token_count is None:
        return None

    return ChunkStatistics(
        char_count=normalized_char_count or len(str(payload.get("content") or "")),
        token_count_estimate=normalized_token_count,
    )


def chunk_type_from_value(value: Any) -> ChunkType:
    try:
        return ChunkType(str(value))
    except Exception:
        return ChunkType.UNKNOWN
