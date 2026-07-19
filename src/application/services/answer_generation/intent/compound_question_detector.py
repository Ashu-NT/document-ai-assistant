from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.intent.answer_intent_vocabulary import (
    CERTIFICATION_TERMS,
    DOCUMENT_SUMMARY_TERMS,
    IDENTIFIER_TERMS,
    MAINTENANCE_TERMS,
    PROCEDURE_TERMS,
    SAFETY_TERMS,
    SPECIFICATION_TERMS,
    TABLE_TERMS,
    TROUBLESHOOTING_TERMS,
)

_COMPOUND_CONJUNCTIONS = (" and ", " also ", " as well as ")
_INTENT_TERM_SETS: dict[AnswerIntent, tuple[str, ...]] = {
    AnswerIntent.SPECIFICATION_SUMMARY: SPECIFICATION_TERMS,
    AnswerIntent.MAINTENANCE_SUMMARY: MAINTENANCE_TERMS,
    AnswerIntent.PROCEDURE_STEPS: PROCEDURE_TERMS,
    AnswerIntent.SAFETY_WARNINGS: SAFETY_TERMS,
    AnswerIntent.TROUBLESHOOTING: TROUBLESHOOTING_TERMS,
    AnswerIntent.CERTIFICATION_SUMMARY: CERTIFICATION_TERMS,
    AnswerIntent.IDENTIFIER_LOOKUP: IDENTIFIER_TERMS,
    AnswerIntent.TABLE_SUMMARY: TABLE_TERMS,
    AnswerIntent.DOCUMENT_SUMMARY: DOCUMENT_SUMMARY_TERMS,
}
_COMPOUND_EXCLUDED_INTENTS_BY_DRIVING: dict[AnswerIntent, frozenset[AnswerIntent]] = {
    AnswerIntent.IDENTIFIER_LOOKUP: frozenset(
        {AnswerIntent.IDENTIFIER_LOOKUP, AnswerIntent.TABLE_SUMMARY}
    ),
    AnswerIntent.TABLE_SUMMARY: frozenset(
        {AnswerIntent.IDENTIFIER_LOOKUP, AnswerIntent.TABLE_SUMMARY}
    ),
}


class CompoundQuestionDetector:
    """Detects a coordinating-conjunction question that mixes two distinct
    answer intents (e.g. "what are the spare parts, and how do I replace
    the seal?"). Used as a pre-dispatch gate: a compound signal means the
    deterministic renderer for the driving intent would only ever answer
    half the question, so generation should route to the LLM instead of
    firing that renderer and disclaiming the rest after the fact (finding
    F3, outputs/architecture/answering_and_prompt_fresh_audit.md)."""

    def detect(
        self,
        *,
        question: str,
        driving_intent: AnswerIntent | None,
    ) -> AnswerIntent | None:
        normalized = " " + " ".join((question or "").strip().lower().split()) + " "
        matched_conjunction = next(
            (
                conjunction
                for conjunction in _COMPOUND_CONJUNCTIONS
                if conjunction in normalized
            ),
            None,
        )
        if matched_conjunction is None:
            return None

        left, _, right = normalized.partition(matched_conjunction)
        excluded_intents = _COMPOUND_EXCLUDED_INTENTS_BY_DRIVING.get(
            driving_intent,
            frozenset({driving_intent}) if driving_intent is not None else frozenset(),
        )
        for half in (left, right):
            for intent, terms in _INTENT_TERM_SETS.items():
                if intent in excluded_intents:
                    continue
                if any(term in half for term in terms):
                    return intent
        return None
