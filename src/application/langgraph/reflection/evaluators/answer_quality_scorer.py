from __future__ import annotations

from typing import Any

from src.application.langgraph.reflection.evaluators.answer_duplicate_content_detector import (
    analyze_duplicate_content,
)
from src.application.langgraph.reflection.evaluators.answer_page_reference_analyzer import (
    analyze_page_references,
)
from src.application.langgraph.reflection.models import AnswerQuality

# A fluent-but-wrong answer must never be indistinguishable from a genuinely
# faithful one just because it also happens to satisfy the lexical/length
# proxies below -- an unresolved (hallucinated) citation caps the score at
# this ceiling regardless of how many of the other signals pass.
_UNRESOLVED_REFERENCE_NOTE_SCORE_CEILING = 0.5


def _reference_note_chunk_id(note: Any) -> str | None:
    """Read `chunk_id` off a reference note, whichever shape it arrives in --
    a serialized dict (the common case, coming off a tool-result payload) or
    a `ReferenceNote` dataclass instance (e.g. in tests that construct one
    directly)."""
    if isinstance(note, dict):
        return note.get("chunk_id")
    return getattr(note, "chunk_id", None)


class AnswerQualityScorer:
    @staticmethod
    def score(
        *,
        question: str,
        answer: str,
        citations: list[dict[str, Any]],
        reference_notes: list[Any] | None = None,
        approved_pages: list[int] | None = None,
    ) -> AnswerQuality:
        normalized_answer = (answer or "").strip()
        answered_question = bool(normalized_answer)
        lower_answer = normalized_answer.lower()
        contains_page_reference = "page" in lower_answer or bool(citations)
        contains_grounding = bool(citations)
        concise_enough = len(normalized_answer) <= 2400 if normalized_answer else False
        question_terms = {
            token
            for token in question.lower().split()
            if len(token) > 3
        }
        answer_terms = set(normalized_answer.lower().split())
        contains_requested_information = bool(question_terms.intersection(answer_terms))
        complete_enough = answered_question and contains_requested_information
        page_analysis = analyze_page_references(
            answer_text=normalized_answer,
            citations=citations,
            approved_pages=list(approved_pages or []),
        )
        duplicate_analysis = analyze_duplicate_content(normalized_answer)
        score = _score(
            answered_question=answered_question,
            contains_requested_information=contains_requested_information,
            contains_page_reference=contains_page_reference,
            contains_grounding=contains_grounding,
            concise_enough=concise_enough,
            complete_enough=complete_enough,
            page_coverage_ratio=page_analysis.coverage_ratio,
            has_unexpected_pages=bool(page_analysis.unexpected_pages),
            has_duplicate_content=duplicate_analysis.has_duplicate_content,
            use_page_scope_scoring=approved_pages is not None,
        )
        issues: list[str] = []
        if not answered_question:
            issues.append("empty_answer")
        if not contains_requested_information:
            issues.append("weak_question_alignment")
        if not contains_grounding:
            issues.append("missing_grounding")
        if page_analysis.unexpected_pages:
            issues.append("unexpected_answer_pages")
        if duplicate_analysis.has_duplicate_content:
            issues.append("duplicate_answer_content")
        if approved_pages is not None and page_analysis.missing_pages:
            issues.append("partial_page_coverage")
        if reference_notes and any(
            _reference_note_chunk_id(note) is None for note in reference_notes
        ):
            # A hallucinated citation (source_number that never resolved to a
            # real chunk) must never coexist with a perfect quality score --
            # cap it, regardless of how many lexical/length signals passed.
            score = round(min(score, _UNRESOLVED_REFERENCE_NOTE_SCORE_CEILING), 4)
            issues.append("unresolved_reference_citation")
        return AnswerQuality(
            answered_question=answered_question,
            contains_requested_information=contains_requested_information,
            contains_page_reference=contains_page_reference,
            contains_grounding=contains_grounding,
            complete_enough=complete_enough,
            concise_enough=concise_enough,
            referenced_pages=page_analysis.referenced_pages,
            unexpected_pages=page_analysis.unexpected_pages,
            missing_pages=page_analysis.missing_pages,
            page_coverage_ratio=page_analysis.coverage_ratio,
            has_duplicate_content=duplicate_analysis.has_duplicate_content,
            duplicate_line_count=duplicate_analysis.duplicate_line_count,
            score=score,
            issues=issues,
        )


def _score(
    *,
    answered_question: bool,
    contains_requested_information: bool,
    contains_page_reference: bool,
    contains_grounding: bool,
    concise_enough: bool,
    complete_enough: bool,
    page_coverage_ratio: float,
    has_unexpected_pages: bool,
    has_duplicate_content: bool,
    use_page_scope_scoring: bool,
) -> float:
    if not use_page_scope_scoring:
        return round(
            (
                (1.0 if answered_question else 0.0)
                + (1.0 if contains_requested_information else 0.0)
                + (1.0 if contains_page_reference else 0.0)
                + (1.0 if contains_grounding else 0.0)
                + (1.0 if concise_enough else 0.0)
                + (1.0 if complete_enough else 0.0)
            )
            / 6.0,
            4,
        )
    return round(
        (
            (1.0 if answered_question else 0.0)
            + (1.0 if contains_requested_information else 0.0)
            + (1.0 if contains_page_reference else 0.0)
            + (1.0 if contains_grounding else 0.0)
            + (1.0 if concise_enough else 0.0)
            + (1.0 if complete_enough else 0.0)
            + (0.0 if has_unexpected_pages else 1.0)
            + page_coverage_ratio
            + (0.0 if has_duplicate_content else 1.0)
        )
        / 9.0,
        4,
    )
