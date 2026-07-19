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
# A numbered-list marker ("1)", "2.", "3:") -- single digit only (a
# technical question enumerating 10+ sub-items is not a realistic case
# worth supporting) and required to be preceded by start-of-string/
# whitespace and followed by whitespace, so a plain number in prose
# ("1000 hours", "at 9 am") can't match: both need a digit run longer than
# one character or no punctuation immediately after the digit.
_ENUMERATED_MARKER = re.compile(r"(?:^|(?<=\s))([1-9])[).:]\s+")


class QuestionClauseSplitter:
    """Splits a question into independent clauses on coordinating
    conjunctions, multi-part question marks, and enumerated-list markers
    (§3.4). A pragmatic v1 heuristic, not full NLP -- it deliberately errs
    toward under-splitting (leaving an ambiguous case as one clause) rather
    than over-splitting a plain noun-phrase conjunction into a false
    multi-clause question."""

    def split(self, question: str | None) -> QuestionClauses:
        normalized = (question or "").strip()
        if not normalized:
            return QuestionClauses(clauses=(normalized,))

        question_mark_clauses = self._split_on_question_marks(normalized)
        if question_mark_clauses is not None:
            return QuestionClauses(clauses=question_mark_clauses)

        enumerated_clauses = self._split_on_enumerated_markers(normalized)
        if enumerated_clauses is not None:
            return QuestionClauses(clauses=enumerated_clauses)

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
    def _split_on_enumerated_markers(question: str) -> tuple[str, ...] | None:
        matches = list(_ENUMERATED_MARKER.finditer(question))
        if len(matches) < 2:
            return None
        numbers = [int(match.group(1)) for match in matches]
        if numbers[0] != 1:
            return None
        if any(numbers[i] <= numbers[i - 1] for i in range(1, len(numbers))):
            return None

        preamble = question[: matches[0].start()].strip()
        clauses: list[str] = []
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(question)
            segment = question[start:end].strip().rstrip(",;")
            if index == 0 and preamble:
                segment = f"{preamble} {segment}".strip()
            if segment:
                clauses.append(segment)
        return tuple(clauses) if len(clauses) > 1 else None

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
