from __future__ import annotations

from collections import OrderedDict
from typing import Sequence

from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerSource,
    AnswerSourceGroup,
)


class SourceGroupBuilder:
    def build(self, sources: Sequence[AnswerSource]) -> list[AnswerSourceGroup]:
        grouped: OrderedDict[str, AnswerSourceGroup] = OrderedDict()
        for source in sources:
            key = source.chunk_type or "general"
            if key not in grouped:
                grouped[key] = AnswerSourceGroup(
                    group_name=self._format_group_name(key),
                    chunk_type=source.chunk_type,
                )
            grouped[key].sources.append(source)
        return list(grouped.values())

    @staticmethod
    def _format_group_name(chunk_type: str) -> str:
        return chunk_type.replace("_", " ").title()
