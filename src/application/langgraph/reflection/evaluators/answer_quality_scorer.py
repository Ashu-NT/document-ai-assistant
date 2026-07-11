from __future__ import annotations

from typing import Any

from src.application.langgraph.reflection.evaluators.maintenance_evidence_relevance_detector import (
    MaintenanceEvidenceRelevanceDetector,
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
    ) -> AnswerQuality:
        normalized_answer = (answer or "").strip()
        answered_question = bool(normalized_answer)
        contains_page_reference = "page" in normalized_answer.lower() or bool(citations)
        contains_grounding = bool(citations)
        concise_enough = len(normalized_answer) <= 2400 if normalized_answer else False
        question_terms = {
            token
            for token in question.lower().split()
            if len(token) > 3
        }
        answer_terms = set(normalized_answer.lower().split())
        contains_requested_information = bool(question_terms.intersection(answer_terms))
        if (
            not contains_requested_information
            and MaintenanceEvidenceRelevanceDetector.question_requests_maintenance_intervals(
                question.lower()
            )
            and MaintenanceEvidenceRelevanceDetector.has_interval_structure(
                normalized_answer.lower()
            )
        ):
            contains_requested_information = True
        complete_enough = answered_question and contains_requested_information
        score = round(
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
        issues: list[str] = []
        if not answered_question:
            issues.append("empty_answer")
        if not contains_requested_information:
            issues.append("weak_question_alignment")
        if not contains_grounding:
            issues.append("missing_grounding")
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
            score=score,
            issues=issues,
        )
