from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AnswerQuality:
    answered_question: bool
    contains_requested_information: bool
    contains_page_reference: bool
    contains_grounding: bool
    complete_enough: bool
    concise_enough: bool
    referenced_pages: list[int]
    unexpected_pages: list[int]
    missing_pages: list[int]
    page_coverage_ratio: float
    has_duplicate_content: bool
    duplicate_line_count: int
    score: float
    issues: list[str] = field(default_factory=list)
