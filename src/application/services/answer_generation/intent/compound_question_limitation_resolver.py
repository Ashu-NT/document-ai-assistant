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
_RENDERER_LIMITATION_LABELS: dict[str, str] = {
    "identifier_answer_renderer": "identifier",
    "spare_parts_list_renderer": "spare parts",
    "maintenance_schedule_renderer": "maintenance schedule",
    "procedure_steps_renderer": "procedure steps",
    "troubleshooting_renderer": "troubleshooting guidance",
    "key_value_fact_sheet_renderer": "structured facts",
}


class CompoundQuestionLimitationResolver:
    def limitation_note(
        self,
        *,
        question: str,
        driving_intent: AnswerIntent | None,
        renderer_name: str,
    ) -> str | None:
        unrelated_intent = self._detect_unrelated_intent_signal(
            question,
            driving_intent,
        )
        if unrelated_intent is None:
            return None
        label = _RENDERER_LIMITATION_LABELS.get(renderer_name, "requested")
        return (
            f"This answer only addresses the {label} portion of your question "
            "â€” ask a follow-up for the rest."
        )

    def _detect_unrelated_intent_signal(
        self,
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
