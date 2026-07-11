from __future__ import annotations

import re

from src.application.langgraph.research.models import ResearchGoalType
from src.application.langgraph.research.planners.concept_strategy_mapper import (
    CATEGORY_PATTERNS,
)
from src.application.langgraph.research.research_text_utils import normalize_theme
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorProposal,
)

_COMPARE_PREFIX_RE = re.compile(
    r"^(?:compare|contrast|difference between|differences between|relationship between|how does)\s+",
    re.IGNORECASE,
)
_SPLIT_RE = re.compile(r"\s+(?:and|versus|vs|with)\s+", re.IGNORECASE)
_FILLER_RE = re.compile(
    r"\b(?:generate|create|build|prepare|produce|give|show|summarize|analyse|analyze|research|report|checklist|document|manual|datasheet|certificate|drawing|all|across|the)\b",
    re.IGNORECASE,
)
_WHITESPACE_RE = re.compile(r"\s+")


def resolve_concepts(
    *,
    user_input: str,
    goal_type: ResearchGoalType,
    advisor_proposal: StrategyAdvisorProposal | None,
) -> list[str]:
    if advisor_proposal is not None and advisor_proposal.concepts:
        return deduplicate_concepts(advisor_proposal.concepts)
    if goal_type == ResearchGoalType.COMPARISON:
        concepts = split_compare_concepts(user_input)
        if concepts:
            return concepts
    keyword_concepts_found = keyword_concepts(user_input)
    if keyword_concepts_found:
        return keyword_concepts_found
    fallback = fallback_focus_phrase(user_input)
    return [fallback] if fallback else ["document evidence"]


def split_compare_concepts(user_input: str) -> list[str]:
    value = _COMPARE_PREFIX_RE.sub("", user_input.strip())
    parts = [clean_phrase(part) for part in _SPLIT_RE.split(value)]
    concepts = [part for part in parts if part]
    return deduplicate_concepts(concepts)


def keyword_concepts(user_input: str) -> list[str]:
    matches: list[str] = []
    value = user_input.strip()
    for pattern, _strategy in CATEGORY_PATTERNS:
        match = pattern.search(value)
        if match is None:
            continue
        phrase = clean_phrase(match.group(0))
        if phrase:
            matches.append(phrase)
    return deduplicate_concepts(matches)


def fallback_focus_phrase(user_input: str) -> str:
    value = _COMPARE_PREFIX_RE.sub("", user_input.strip())
    value = _FILLER_RE.sub(" ", value)
    return clean_phrase(value)


def clean_phrase(value: str) -> str:
    cleaned = _FILLER_RE.sub(" ", value)
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip(" ,.;:-")
    return cleaned


def deduplicate_concepts(concepts: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for concept in concepts:
        normalized = normalize_theme(concept)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(concept)
    return ordered


def concept_list_text(concepts: list[str]) -> str:
    if not concepts:
        return "the request topics"
    if len(concepts) == 1:
        return concepts[0]
    return ", ".join(concepts[:-1]) + f", and {concepts[-1]}"
