from __future__ import annotations

from dataclasses import replace

from src.application.prompts.answer_generation.prompt_context.appendix.prompt_budget_allocator import (
    PromptBudgetAllocator,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_context_bundle import (
    PromptContextBundle,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)


class RawSourceInclusionPolicy:
    def __init__(
        self,
        prompt_budget_allocator: PromptBudgetAllocator | None = None,
    ) -> None:
        self.prompt_budget_allocator = prompt_budget_allocator or PromptBudgetAllocator()

    def select(self, context: PromptContextBundle | None) -> list[PromptSourceView]:
        if context is None:
            return []
        sources = list(context.appendix_sources or context.sources)
        if not sources:
            return []
        budget = self.prompt_budget_allocator.allocate(context)
        if budget.max_sources <= 0 or budget.max_chars_per_source <= 0:
            return []
        roles = self._roles_by_source_number(context)
        ranked_sources = sorted(
            sources,
            key=lambda source: (
                self._role_rank(roles.get(source.source_number, "supporting")),
                -(source.score if source.score is not None else float("-inf")),
                source.source_number,
            ),
        )
        return [
            replace(
                source,
                content=self._truncate(source.content, budget.max_chars_per_source),
            )
            for source in ranked_sources[: budget.max_sources]
        ]

    @staticmethod
    def _roles_by_source_number(context: PromptContextBundle) -> dict[int, str]:
        roles: dict[int, str] = {}
        for family in context.source_families:
            for source_number in family.direct_source_numbers:
                roles[source_number] = "direct"
            for source_number in family.supporting_source_numbers:
                roles.setdefault(source_number, "supporting")
            for source_number in family.contextual_source_numbers:
                roles.setdefault(source_number, "contextual")
        return roles

    @staticmethod
    def _role_rank(role: str) -> int:
        return {
            "direct": 0,
            "supporting": 1,
            "contextual": 2,
        }.get(role, 1)

    @staticmethod
    def _truncate(content: str, max_chars: int) -> str:
        normalized = (content or "").strip()
        if len(normalized) <= max_chars:
            return normalized
        truncated = normalized[: max_chars + 1].rsplit(" ", maxsplit=1)[0].strip()
        if not truncated:
            truncated = normalized[:max_chars].strip()
        return f"{truncated}..."
