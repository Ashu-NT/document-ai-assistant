from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.table_focus import is_table_focused_query
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery


def _make_query(
    *,
    query_text: str,
    detected_intent: str | None = None,
    chunk_types: list[ChunkType] | None = None,
) -> RetrievalQuery:
    return RetrievalQuery(
        query_id="rq_001",
        query_text=query_text,
        detected_intent=detected_intent,
        chunk_types=chunk_types or [],
        analyzed=True,
    )


def test_table_intent_is_always_table_focused() -> None:
    query = _make_query(query_text="show spare parts", detected_intent="table")

    assert is_table_focused_query(query=query) is True


def test_maintenance_interval_wording_is_table_focused() -> None:
    query = _make_query(
        query_text="What are the maintenance intervals schedule table?",
        detected_intent="maintenance",
        chunk_types=[ChunkType.MAINTENANCE_INTERVAL],
    )

    assert (
        is_table_focused_query(query=query, intent=RetrievalQueryIntent.MAINTENANCE)
        is True
    )


def test_general_overview_query_is_not_table_focused() -> None:
    query = _make_query(
        query_text="What is the purpose of the pump?",
        detected_intent="overview",
        chunk_types=[ChunkType.OVERVIEW],
    )

    assert is_table_focused_query(query=query) is False
