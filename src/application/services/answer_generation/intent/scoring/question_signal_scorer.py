from __future__ import annotations

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.services.answer_generation.intent.scoring.answer_intent_vocabulary import (
    CERTIFICATION_TERMS,
    DOCUMENT_SUMMARY_TERMS,
    EXPLICIT_PROCEDURE_PHRASES,
    IDENTIFIER_LISTING_MARKERS,
    IDENTIFIER_LISTING_VERBS,
    IDENTIFIER_TERMS,
    MAINTENANCE_SUMMARY_PHRASES,
    MAINTENANCE_TERMS,
    PROCEDURE_TERMS,
    RETRIEVAL_INTENT_TO_ANSWER_INTENT,
    SAFETY_TERMS,
    SPARE_PARTS_LIST_PHRASES,
    SPECIFICATION_TERMS,
    TABLE_TERMS,
    TROUBLESHOOTING_TERMS,
)
from src.application.workflows.shared.negation_detection import (
    has_non_negated_occurrence,
)


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def _score_terms(
    text: str,
    intent: AnswerIntent,
    terms: tuple[str, ...],
    weight: int,
    scores: dict[AnswerIntent, int],
    matched: dict[AnswerIntent, list[str]],
) -> None:
    # Negation-aware: a term preceded by a negation cue ("not", "without",
    # "unrelated to", ...) within a short lookback window doesn't
    # contribute to its intent's score -- e.g. "this is not a maintenance
    # question" no longer scores MAINTENANCE_SUMMARY. Shares the exact
    # cue vocabulary/lookback logic RetrievalQueryIntentInferer uses via
    # negation_detection.has_non_negated_occurrence.
    for term in terms:
        if has_non_negated_occurrence(text, term):
            scores[intent] += weight
            matched[intent].append(f"question:{term}")


def _contains_identifier_reference(question: str) -> bool:
    return any(marker in question for marker in IDENTIFIER_LISTING_MARKERS)


def _looks_like_identifier_listing_question(question: str) -> bool:
    if not any(marker in question for marker in IDENTIFIER_LISTING_VERBS):
        return False
    return _contains_identifier_reference(question)


def looks_like_maintenance_question(question: str) -> bool:
    return "maintenance" in question or any(
        phrase in question for phrase in MAINTENANCE_SUMMARY_PHRASES
    )


def looks_like_explicit_procedure_question(question: str) -> bool:
    return any(phrase in question for phrase in EXPLICIT_PROCEDURE_PHRASES)


def looks_like_specification_question(question: str) -> bool:
    return any(term in question for term in SPECIFICATION_TERMS)


def apply_question_signals(
    question: str,
    scores: dict[AnswerIntent, int],
    matched: dict[AnswerIntent, list[str]],
) -> None:
    _score_terms(
        question,
        AnswerIntent.SPECIFICATION_SUMMARY,
        SPECIFICATION_TERMS,
        6,
        scores,
        matched,
    )
    _score_terms(
        question,
        AnswerIntent.MAINTENANCE_SUMMARY,
        MAINTENANCE_TERMS,
        6,
        scores,
        matched,
    )
    _score_terms(
        question,
        AnswerIntent.PROCEDURE_STEPS,
        PROCEDURE_TERMS,
        6,
        scores,
        matched,
    )
    _score_terms(
        question,
        AnswerIntent.SAFETY_WARNINGS,
        SAFETY_TERMS,
        6,
        scores,
        matched,
    )
    _score_terms(
        question,
        AnswerIntent.TROUBLESHOOTING,
        TROUBLESHOOTING_TERMS,
        6,
        scores,
        matched,
    )
    _score_terms(
        question,
        AnswerIntent.CERTIFICATION_SUMMARY,
        CERTIFICATION_TERMS,
        6,
        scores,
        matched,
    )
    _score_terms(
        question,
        AnswerIntent.IDENTIFIER_LOOKUP,
        IDENTIFIER_TERMS,
        6,
        scores,
        matched,
    )
    _score_terms(
        question,
        AnswerIntent.TABLE_SUMMARY,
        TABLE_TERMS,
        5,
        scores,
        matched,
    )
    _score_terms(
        question,
        AnswerIntent.DOCUMENT_SUMMARY,
        DOCUMENT_SUMMARY_TERMS,
        5,
        scores,
        matched,
    )
    if "how often" in question:
        scores[AnswerIntent.MAINTENANCE_SUMMARY] += 3
        matched[AnswerIntent.MAINTENANCE_SUMMARY].append("question:how often")
    if any(phrase in question for phrase in MAINTENANCE_SUMMARY_PHRASES):
        scores[AnswerIntent.MAINTENANCE_SUMMARY] += 4
        matched[AnswerIntent.MAINTENANCE_SUMMARY].append(
            "question:maintenance_summary_phrase"
        )
    if "what is in" in question or "what's in" in question:
        scores[AnswerIntent.DOCUMENT_SUMMARY] += 2
        matched[AnswerIntent.DOCUMENT_SUMMARY].append("question:what is in")
    if _contains_identifier_reference(question):
        scores[AnswerIntent.IDENTIFIER_LOOKUP] += 3
        matched[AnswerIntent.IDENTIFIER_LOOKUP].append(
            "question:identifier_reference"
        )
    if _looks_like_identifier_listing_question(question):
        scores[AnswerIntent.IDENTIFIER_LOOKUP] += 8
        matched[AnswerIntent.IDENTIFIER_LOOKUP].append(
            "question:identifier_listing_request"
        )
    if any(phrase in question for phrase in SPARE_PARTS_LIST_PHRASES):
        scores[AnswerIntent.TABLE_SUMMARY] += 10
        matched[AnswerIntent.TABLE_SUMMARY].append(
            "question:spare_parts_list_phrase"
        )


def apply_route_signal(
    route: str | None,
    scores: dict[AnswerIntent, int],
    matched: dict[AnswerIntent, list[str]],
) -> None:
    if route == "document_exploration":
        scores[AnswerIntent.DOCUMENT_SUMMARY] += 5
        matched[AnswerIntent.DOCUMENT_SUMMARY].append("route:document_exploration")


def apply_retrieval_intent_signal(
    retrieval_intent: str | None,
    scores: dict[AnswerIntent, int],
    matched: dict[AnswerIntent, list[str]],
) -> None:
    normalized = normalize_text(retrieval_intent)
    answer_intent = RETRIEVAL_INTENT_TO_ANSWER_INTENT.get(normalized)
    if answer_intent is None:
        return
    scores[answer_intent] += 4
    matched[answer_intent].append(f"retrieval:{normalized}")


def apply_maintenance_procedure_disambiguation(
    question: str,
    scores: dict[AnswerIntent, int],
    matched: dict[AnswerIntent, list[str]],
) -> None:
    if not looks_like_maintenance_question(question):
        return
    if looks_like_explicit_procedure_question(question):
        scores[AnswerIntent.PROCEDURE_STEPS] += 2
        matched[AnswerIntent.PROCEDURE_STEPS].append(
            "question:explicit_procedure_request"
        )
        return
    scores[AnswerIntent.MAINTENANCE_SUMMARY] += 4
    matched[AnswerIntent.MAINTENANCE_SUMMARY].append(
        "question:maintenance_over_procedure"
    )
