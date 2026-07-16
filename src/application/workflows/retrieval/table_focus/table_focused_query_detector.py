from src.application.workflows.retrieval.intent.retrieval_query_intent_markers import (
    IDENTIFIER_TABLE_MARKERS,
    SPECIFICATION_TABLE_MARKERS,
    TABLE_REQUEST_MARKERS,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.shared.maintenance_signal_detection import (
    MAINTENANCE_INTERVAL_MARKERS,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery

_TABLE_FOCUSED_CHUNK_TYPES = {
    ChunkType.SPARE_PARTS_TABLE,
    ChunkType.TECHNICAL_SPECIFICATION,
    ChunkType.CERTIFICATION_INFO,
    ChunkType.MAINTENANCE_INTERVAL,
    ChunkType.TROUBLESHOOTING,
}


def is_table_focused_query(
    *,
    query: RetrievalQuery,
    intent: RetrievalQueryIntent | None = None,
) -> bool:
    query_text = query.effective_query().lower()
    resolved_intent = intent or _coerce_intent(query.detected_intent)

    if resolved_intent == RetrievalQueryIntent.TABLE:
        return True
    if resolved_intent == RetrievalQueryIntent.MAINTENANCE:
        return _has_any_marker(query_text, MAINTENANCE_INTERVAL_MARKERS)
    if resolved_intent == RetrievalQueryIntent.SPECIFICATION:
        return _has_any_marker(query_text, SPECIFICATION_TABLE_MARKERS)
    if resolved_intent == RetrievalQueryIntent.IDENTIFIER:
        return _has_any_marker(query_text, IDENTIFIER_TABLE_MARKERS)
    if resolved_intent == RetrievalQueryIntent.TROUBLESHOOTING:
        return _has_any_marker(query_text, TABLE_REQUEST_MARKERS)

    return bool(
        query.chunk_types
        and any(
            chunk_type in _TABLE_FOCUSED_CHUNK_TYPES
            for chunk_type in query.chunk_types
        )
        and _has_any_marker(query_text, TABLE_REQUEST_MARKERS)
    )


def _coerce_intent(raw_value: str | None) -> RetrievalQueryIntent | None:
    if not raw_value:
        return None
    try:
        return RetrievalQueryIntent(raw_value)
    except ValueError:
        return None


def _has_any_marker(query_text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in query_text for marker in markers)
