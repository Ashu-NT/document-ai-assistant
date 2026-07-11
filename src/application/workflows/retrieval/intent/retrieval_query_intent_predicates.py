import re

from src.application.workflows.retrieval.intent.retrieval_query_intent_markers import (
    COMPARATIVE_MARKERS,
    EXPLICIT_IDENTIFIER_PATTERNS,
    EXPLORATION_PATTERNS,
    IDENTIFIER_LISTING_MARKERS,
    IDENTIFIER_LISTING_VERBS,
)
from src.domain.retrieval import RetrievalQuery


def is_document_exploration(query_text: str) -> bool:
    for pattern in EXPLORATION_PATTERNS:
        if pattern.search(query_text):
            return True
    return False


def is_explicit_identifier_lookup(
    query_text: str,
    query: RetrievalQuery | None,
) -> bool:
    if any(pattern.search(query_text) for pattern in EXPLICIT_IDENTIFIER_PATTERNS):
        return True

    if query is None or not query.has_identifiers():
        return False

    if any(
        marker in query_text
        for marker in (
            " mean",
            " means",
            "meaning",
            "stand for",
            "stands for",
            "designation",
            "position ",
            "type ",
        )
    ):
        return True

    return bool(
        re.search(r"\bwhat\s+does\s+[a-z0-9-]+\s+mean\b", query_text)
        or re.search(r"\bwhat\s+is\s+position\s+[a-z0-9-]+\b", query_text)
    )


def _contains_identifier_reference(query_text: str) -> bool:
    return any(marker in query_text for marker in IDENTIFIER_LISTING_MARKERS)


def looks_like_identifier_listing_query(query_text: str) -> bool:
    if not any(marker in query_text for marker in IDENTIFIER_LISTING_VERBS):
        return False
    return _contains_identifier_reference(query_text)


def is_comparative_query(query_text: str) -> bool:
    return any(marker in query_text for marker in COMPARATIVE_MARKERS)
