from __future__ import annotations

import re
from typing import Sequence

from src.domain.assets import TableAsset, TableCellSpan
from src.domain.common import BoundingBox
from src.domain.retrieval import RowBoundingBox

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


class TableRowBboxMatcher:
    def match(
        self,
        *,
        table: TableAsset,
        query_text: str,
        identifier_values: Sequence[str],
    ) -> list[RowBoundingBox] | None:
        query_tokens = _meaningful_tokens(query_text)
        if not query_tokens:
            return None
        if not table.rows:
            return None

        scores = [
            self._score_row(row, query_tokens=query_tokens, identifier_values=identifier_values)
            for row in table.rows
        ]
        best_score = max(scores)
        if best_score <= 0:
            return None

        row_bboxes: list[RowBoundingBox] = []
        for row_index, score in enumerate(scores):
            if score != best_score:
                continue
            row_bboxes.extend(self._row_bboxes(table=table, row_index=row_index))

        return row_bboxes or None

    @staticmethod
    def _score_row(
        row: Sequence[str],
        *,
        query_tokens: set[str],
        identifier_values: Sequence[str],
    ) -> int:
        row_text = " ".join(str(cell) for cell in row if str(cell).strip())
        row_tokens = _meaningful_tokens(row_text)
        token_score = sum(1 for token in query_tokens if token in row_tokens)

        lowered_row_text = row_text.lower()
        identifier_score = sum(
            1
            for identifier in identifier_values
            if identifier.strip() and identifier.lower() in lowered_row_text
        )
        return token_score + identifier_score

    @staticmethod
    def _row_bboxes(*, table: TableAsset, row_index: int) -> list[RowBoundingBox]:
        row = table.rows[row_index]
        matched_spans: list[TableCellSpan] = []
        for cell_text in row:
            normalized_cell = _normalize_text(cell_text)
            if not normalized_cell:
                continue
            matched_spans.extend(
                span
                for span in table.cell_spans
                if _normalize_text(span.normalized_text or span.text) == normalized_cell
            )

        bboxes_by_page: dict[int | None, list[BoundingBox]] = {}
        for span in matched_spans:
            if span.bbox is None:
                continue
            bboxes_by_page.setdefault(span.page_number, []).append(span.bbox)

        return [
            RowBoundingBox(
                row_index=row_index,
                page_number=page_number,
                bbox=BoundingBox(
                    x1=min(bbox.x1 for bbox in bboxes),
                    y1=min(bbox.y1 for bbox in bboxes),
                    x2=max(bbox.x2 for bbox in bboxes),
                    y2=max(bbox.y2 for bbox in bboxes),
                ),
            )
            for page_number, bboxes in bboxes_by_page.items()
        ]


def _meaningful_tokens(text: str) -> set[str]:
    tokens = {
        _singularize(token)
        for token in _TOKEN_RE.findall((text or "").lower())
        if token not in _STOPWORDS and len(token) > 2
    }
    return {token for token in tokens if token}


def _singularize(token: str) -> str:
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token


def _normalize_text(text: str | None) -> str:
    return " ".join(str(text or "").split()).lower()
