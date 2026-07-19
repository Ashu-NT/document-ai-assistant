from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

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
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

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

if TYPE_CHECKING:
    from src.application.langgraph.reflection.decomposition import (
        QuestionClauseSplitter,
    )

# Mirrors QuestionClauseSplitter's own "does this question carry a real
# multi-part question-mark boundary, not just one trailing '?'" check --
# duplicated (not imported) because it's only used here to label *why* a
# split happened for diagnostics, never to decide whether to split at all;
# the splitter itself remains the single source of truth for that.
_QUESTION_MARK = re.compile(r"\?+")


@dataclass(frozen=True, slots=True)
class CompoundQuestionSignal:
    """Structured compound-question signal (PR 6,
    answering_flow_weakness_remediation_plan.md) -- replaces the old bare
    `AnswerIntent | None` return value so callers can log *why* a question
    was flagged compound and *what* it split into, not just that it was."""

    is_compound: bool
    reason: str | None = None
    unrelated_intent: AnswerIntent | None = None
    clauses: tuple[str, ...] | None = None


class CompoundQuestionDetector:
    """Detects a question that splits into two or more independently
    answerable clauses carrying distinct answer intents (e.g. "what are the
    spare parts, and how do I replace the seal?"). Used as a pre-dispatch
    gate: a compound signal means the deterministic renderer for the
    driving intent would only ever answer part of the question, so
    generation should route to the LLM instead of firing that renderer and
    disclaiming the rest after the fact (finding F3,
    outputs/architecture/answering_and_prompt_fresh_audit.md).

    Reuses `QuestionClauseSplitter` (built for reflection's multi-clause
    coverage scoring) for the actual splitting -- explicit conjunctions AND
    multi-part question marks -- instead of maintaining a second, narrower
    conjunction-only splitter. This also inherits the splitter's
    noun-phrase false-positive guard for free: "inspection and
    certification requirements" stays one clause because "certification
    requirements" doesn't start with a question trigger word."""

    def __init__(
        self,
        *,
        clause_splitter: "QuestionClauseSplitter | None" = None,
    ) -> None:
        if clause_splitter is None:
            # Deferred: a module-level import of
            # src.application.langgraph.reflection.decomposition re-enters
            # the src.application.langgraph package's __init__ chain, which
            # imports back into this module via
            # answer_generation_service.py -> deterministic_dispatch_gate.py
            # -- a genuine circular import. Constructed lazily here instead,
            # by which point that whole chain has already finished loading.
            from src.application.langgraph.reflection.decomposition import (
                QuestionClauseSplitter,
            )

            clause_splitter = QuestionClauseSplitter()
        self._clause_splitter = clause_splitter

    def detect(
        self,
        *,
        question: str,
        driving_intent: AnswerIntent | None,
    ) -> CompoundQuestionSignal:
        if not question or not question.strip():
            return CompoundQuestionSignal(is_compound=False)

        clauses = self._clause_splitter.split(question)
        if not clauses.has_multiple_clauses:
            return CompoundQuestionSignal(is_compound=False)

        excluded_intents = _COMPOUND_EXCLUDED_INTENTS_BY_DRIVING.get(
            driving_intent,
            frozenset({driving_intent}) if driving_intent is not None else frozenset(),
        )
        unrelated_intent = _find_unrelated_intent(clauses.clauses, excluded_intents)
        if unrelated_intent is None:
            return CompoundQuestionSignal(is_compound=False)

        reason = (
            "multi_question_mark"
            if _has_multiple_question_marks(question)
            else "conjunction"
        )
        return CompoundQuestionSignal(
            is_compound=True,
            reason=reason,
            unrelated_intent=unrelated_intent,
            clauses=clauses.clauses,
        )


def _find_unrelated_intent(
    clauses: tuple[str, ...],
    excluded_intents: frozenset[AnswerIntent],
) -> AnswerIntent | None:
    for clause in clauses:
        normalized_clause = clause.strip().lower()
        for intent, terms in _INTENT_TERM_SETS.items():
            if intent in excluded_intents:
                continue
            if any(term in normalized_clause for term in terms):
                return intent
    return None


def _has_multiple_question_marks(question: str) -> bool:
    marks = list(_QUESTION_MARK.finditer(question))
    only_one_trailing_mark = len(marks) == 1 and marks[0].end() >= len(
        question.rstrip()
    )
    return len(marks) >= 1 and not only_one_trailing_mark


def chunks_plausibly_cover_intent(
    chunks: Sequence[RetrievedChunk],
    intent: AnswerIntent | None,
) -> bool:
    """A cheap, non-authoritative proxy for "did retrieval actually bring
    back evidence for the compound question's *unrelated* clause" -- PR 6's
    explicitly-required logging signal, not a retrieval redesign (see
    answering_flow_weakness_remediation_plan.md's "Retrieval limitation,
    explicitly deferred" note). Compound detection runs on the question
    text alone and has no way to know whether the chunks a single retrieval
    pass already fetched happen to also cover the second, unrelated intent
    it found -- this just checks for the same term vocabulary
    `_find_unrelated_intent` matched on, applied to chunk content instead
    of question text, so a dashboard can distinguish "compound question,
    plausibly answerable anyway" from "compound question, evidence gap"."""
    if intent is None:
        return False
    terms = _INTENT_TERM_SETS.get(intent, ())
    if not terms:
        return False
    return any(
        term in chunk.content.lower() for chunk in chunks for term in terms
    )
