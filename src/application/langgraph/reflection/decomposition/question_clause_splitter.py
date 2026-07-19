from __future__ import annotations

import re

from src.application.langgraph.reflection.decomposition.question_clauses import (
    QuestionClauses,
)

# Guards the conjunction split: "and"/"as well as" only starts a genuine new
# clause when what follows looks like its own question, not a noun-phrase
# conjunction ("maintenance tasks and intervals" must stay one clause).
_QUESTION_TRIGGER_WORDS = frozenset(
    {
        "what", "which", "how", "when", "where", "why", "who",
        "is", "are", "was", "were", "do", "does", "did",
        "can", "could", "should", "will", "would", "has", "have",
    }
)

_CONJUNCTION_SPLIT = re.compile(r",?\s+(?:and|as well as)\s+", re.IGNORECASE)
_QUESTION_MARK = re.compile(r"\?+")


class QuestionClauseSplitter:
    """Splits a question into independent clauses on coordinating
    conjunctions and multi-part question marks (§3.4). A pragmatic v1
    heuristic, not full NLP -- it deliberately errs toward under-splitting
    (leaving an ambiguous case as one clause) rather than over-splitting a
    plain noun-phrase conjunction into a false multi-clause question."""

    def split(self, question: str | None) -> QuestionClauses:
        normalized = (question or "").strip()
        if not normalized:
            return QuestionClauses(clauses=(normalized,))

        question_mark_clauses = self._split_on_question_marks(normalized)
        if question_mark_clauses is not None:
            return QuestionClauses(clauses=question_mark_clauses)

        conjunction_clauses = self._split_on_conjunctions(normalized)
        return QuestionClauses(clauses=conjunction_clauses or (normalized,))

    @staticmethod
    def _split_on_question_marks(question: str) -> tuple[str, ...] | None:
        marks = list(_QUESTION_MARK.finditer(question))
        only_one_trailing_mark = len(marks) == 1 and marks[0].end() >= len(
            question.rstrip()
        )
        if len(marks) < 1 or only_one_trailing_mark:
            return None
        parts: list[str] = []
        start = 0
        for match in marks:
            segment = question[start : match.end()].strip()
            if segment:
                parts.append(segment)
            start = match.end()
        trailing = question[start:].strip()
        if trailing:
            parts.append(trailing)
        return tuple(parts) if len(parts) > 1 else None

    @staticmethod
    def _split_on_conjunctions(question: str) -> tuple[str, ...] | None:
        raw_parts = _CONJUNCTION_SPLIT.split(question)
        if len(raw_parts) < 2:
            return None
        clauses: list[str] = [raw_parts[0].strip()]
        for part in raw_parts[1:]:
            stripped = part.strip()
            first_word = (
                stripped.split(" ", 1)[0].strip("?,.").lower() if stripped else ""
            )
            # A "?" only reaches this path (see split() above) as the
            # sentence's own single trailing mark, never a genuine second
            # question boundary -- so only the trigger-word check can prove
            # a real new clause here.
            if first_word in _QUESTION_TRIGGER_WORDS:
                clauses.append(stripped)
            else:
                clauses[-1] = f"{clauses[-1]} and {stripped}".strip()
        non_empty = tuple(clause for clause in clauses if clause)
        return non_empty if len(non_empty) > 1 else None
