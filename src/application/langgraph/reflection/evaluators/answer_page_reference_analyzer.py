from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

_PAGE_REF_RE = re.compile(
    r"\b(?:pp?\.\s*|pages?\s+)(\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*)",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class AnswerPageReferenceAnalysis:
    referenced_pages: list[int]
    unexpected_pages: list[int]
    missing_pages: list[int]
    coverage_ratio: float


def analyze_page_references(
    *,
    answer_text: str,
    citations: list[dict[str, Any]],
    approved_pages: list[int],
) -> AnswerPageReferenceAnalysis:
    referenced = sorted(
        _pages_from_text(answer_text).union(_pages_from_citations(citations))
    )
    approved = sorted(set(approved_pages))
    referenced_set = set(referenced)
    approved_set = set(approved)
    unexpected = sorted(referenced_set - approved_set)
    missing = sorted(approved_set - referenced_set)
    coverage_ratio = 1.0
    if approved:
        coverage_ratio = len(referenced_set & approved_set) / len(approved_set)
    return AnswerPageReferenceAnalysis(
        referenced_pages=referenced,
        unexpected_pages=unexpected,
        missing_pages=missing,
        coverage_ratio=round(coverage_ratio, 4),
    )


def _pages_from_text(answer_text: str) -> set[int]:
    pages: set[int] = set()
    for match in _PAGE_REF_RE.finditer(answer_text or ""):
        for token in match.group(1).split(","):
            pages.update(_expand_token(token))
    return pages


def _pages_from_citations(citations: list[dict[str, Any]]) -> set[int]:
    pages: set[int] = set()
    for citation in citations:
        source = citation.get("source") if isinstance(citation, dict) else None
        if isinstance(source, dict):
            pages.update(_expand_bounds(source.get("page_start"), source.get("page_end")))
            continue
        pages.update(
            _expand_bounds(
                citation.get("page_start") if isinstance(citation, dict) else None,
                citation.get("page_end") if isinstance(citation, dict) else None,
            )
        )
    return pages


def _expand_token(token: str) -> set[int]:
    cleaned = token.strip().replace("–", "-")
    if "-" not in cleaned:
        try:
            return {int(cleaned)}
        except ValueError:
            return set()
    start_text, end_text = [part.strip() for part in cleaned.split("-", maxsplit=1)]
    try:
        start = int(start_text)
        end = int(end_text)
    except ValueError:
        return set()
    return _expand_bounds(start, end)


def _expand_bounds(start: Any, end: Any) -> set[int]:
    if not isinstance(start, int):
        return set()
    if not isinstance(end, int) or end < start:
        end = start
    return set(range(start, end + 1))
