from __future__ import annotations

import re

from src.application.services.answer_generation.intent.scoring.answer_intent_vocabulary import (
    CERTIFICATION_TERMS,
    IDENTIFIER_TERMS,
    MAINTENANCE_TERMS,
    PROCEDURE_TERMS,
    SPECIFICATION_TERMS,
    TABLE_TERMS,
    TROUBLESHOOTING_TERMS,
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_CATEGORY_ALIASES: dict[str, frozenset[str]] = {
    "maintenance": frozenset({"maintenance", "service", "servicing", "inspection"}),
    "troubleshooting": frozenset(
        {"troubleshooting", "troubleshoot", "fault", "failure", "recovery", "remedy"}
    ),
    "procedure": frozenset({"procedure", "procedures", "step", "steps", "operation"}),
    "specification": frozenset({"specification", "specifications", "spec", "technical"}),
    "identifier": frozenset({"identifier", "identifiers", "serial", "part", "model"}),
    "table": frozenset({"table", "tables", "list", "lists", "matrix", "schedule"}),
    "certification": frozenset({"certificate", "certification", "approval", "compliance"}),
}
_CATEGORY_QUERY_TERMS: dict[str, tuple[str, ...]] = {
    "maintenance": MAINTENANCE_TERMS,
    "troubleshooting": TROUBLESHOOTING_TERMS,
    "procedure": PROCEDURE_TERMS,
    "specification": SPECIFICATION_TERMS,
    "identifier": IDENTIFIER_TERMS,
    "table": TABLE_TERMS,
    "certification": CERTIFICATION_TERMS,
}


def is_grounded_concept(*, concept: str, query_text: str) -> bool:
    concept_tokens = _normalized_tokens(concept)
    query_tokens = _normalized_tokens(query_text)
    if not concept_tokens or not query_tokens:
        return False
    if concept_tokens.issubset(query_tokens):
        return True

    concept_categories = _matched_categories(concept_tokens)
    query_categories = _matched_query_categories(query_text)
    if concept_categories and concept_categories.intersection(query_categories):
        return True

    overlap = concept_tokens.intersection(query_tokens)
    return bool(overlap) and len(overlap) >= max(1, len(concept_tokens) // 2)


def _matched_categories(tokens: set[str]) -> set[str]:
    return {
        category
        for category, aliases in _CATEGORY_ALIASES.items()
        if tokens.intersection({_normalize_token(alias) for alias in aliases})
    }


def _matched_query_categories(query_text: str) -> set[str]:
    categories: set[str] = set()
    normalized_query = " ".join(_normalized_sequence(query_text))
    for category, terms in _CATEGORY_QUERY_TERMS.items():
        for term in terms:
            normalized_term = " ".join(_normalized_tokens(term))
            if normalized_term and normalized_term in normalized_query:
                categories.add(category)
                break
    return categories


def _normalized_tokens(text: str) -> set[str]:
    return {_normalize_token(token) for token in _TOKEN_RE.findall((text or "").lower())}


def _normalized_sequence(text: str) -> list[str]:
    return [_normalize_token(token) for token in _TOKEN_RE.findall((text or "").lower())]


def _normalize_token(token: str) -> str:
    normalized = token.strip().lower()
    for suffix in ("ing", "ed", "es", "s"):
        if len(normalized) > 4 and normalized.endswith(suffix):
            return normalized[: -len(suffix)]
    return normalized
