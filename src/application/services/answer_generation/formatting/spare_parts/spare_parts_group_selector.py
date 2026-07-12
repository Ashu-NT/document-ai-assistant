from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from src.application.services.answer_generation.formatting.spare_parts.spare_parts_group import (
    SparePartsGroup,
)

_STOPWORDS = frozenset(
    {
        "all",
        "for",
        "list",
        "lists",
        "of",
        "part",
        "parts",
        "show",
        "spare",
        "table",
        "tables",
        "the",
    }
)
_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True, slots=True)
class SparePartsSelectionResult:
    groups: list[SparePartsGroup]
    narrowed: bool


class SparePartsGroupSelector:
    def select(
        self,
        *,
        question: str,
        groups: Sequence[SparePartsGroup],
    ) -> SparePartsSelectionResult:
        group_list = list(groups)
        if len(group_list) <= 1:
            return SparePartsSelectionResult(groups=group_list, narrowed=bool(group_list))

        query_tokens = _meaningful_tokens(question)
        if not query_tokens:
            return SparePartsSelectionResult(groups=group_list, narrowed=False)

        scored = [
            (self._score_group(group, query_tokens), group)
            for group in group_list
        ]
        best_score = max(score for score, _ in scored)
        if best_score <= 0:
            return SparePartsSelectionResult(groups=group_list, narrowed=False)

        selected = [group for score, group in scored if score == best_score]
        return SparePartsSelectionResult(
            groups=selected,
            narrowed=len(selected) < len(group_list),
        )

    @staticmethod
    def _score_group(group: SparePartsGroup, query_tokens: set[str]) -> int:
        group_tokens = _group_tokens(group)
        return sum(1 for token in query_tokens if token in group_tokens)


def _meaningful_tokens(text: str) -> set[str]:
    tokens = {
        _singularize(token)
        for token in _TOKEN_RE.findall((text or "").lower())
        if token not in _STOPWORDS and len(token) > 2
    }
    return {token for token in tokens if token}


def _group_tokens(group: SparePartsGroup) -> set[str]:
    parts = [group.section_title, group.section_path or ""]
    for row in group.rows:
        parts.extend(str(value) for value in row.values() if str(value).strip())
    combined = " ".join(parts)
    return _meaningful_tokens(combined)


def _singularize(token: str) -> str:
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token
