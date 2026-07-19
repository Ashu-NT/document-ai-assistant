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
        sources, _diagnostics = self.select_with_diagnostics(context)
        return sources

    def select_with_diagnostics(
        self, context: PromptContextBundle | None
    ) -> tuple[list[PromptSourceView], dict[str, object]]:
        """Same as `select()`, but also returns truncation diagnostics
        (`selected_count`/`total_count`/`omitted_count`/`truncated`/
        `truncation_reason`, plus which source_numbers had their content
        cut by the char budget) -- PR 8, W6,
        answering_flow_weakness_remediation_plan.md. `select()` stays a
        thin wrapper so its existing callers/tests don't need to change."""
        if context is None:
            return [], _no_truncation_diagnostics()
        sources = list(context.appendix_sources or context.sources)
        # A source with no narrative content would occupy one of the very
        # few raw-appendix slots while printing nothing but a bare header,
        # AND its source_number would still land in appendix_source_numbers
        # -- incorrectly counting as "content was shown as raw text" for
        # citation resolution even though the model saw no actual
        # evidentiary text for it (finding F9,
        # outputs/architecture/answering_and_prompt_fresh_audit.md).
        sources = [source for source in sources if (source.content or "").strip()]
        if not sources:
            return [], _no_truncation_diagnostics()
        budget = self.prompt_budget_allocator.allocate(context)
        if budget.max_sources <= 0 or budget.max_chars_per_source <= 0:
            return [], _source_count_diagnostics(total_count=len(sources), selected_count=0)
        roles = self._roles_by_source_number(context)
        ranked_sources = sorted(
            sources,
            key=lambda source: (
                self._role_rank(roles.get(source.source_number, "supporting")),
                -(source.score if source.score is not None else float("-inf")),
                source.source_number,
            ),
        )
        selected_ranked = ranked_sources[: budget.max_sources]
        char_truncated_source_numbers = [
            source.source_number
            for source in selected_ranked
            if len((source.content or "").strip()) > budget.max_chars_per_source
        ]
        selected = [
            replace(
                source,
                content=self._truncate(source.content, budget.max_chars_per_source),
            )
            for source in selected_ranked
        ]
        diagnostics = _source_count_diagnostics(
            total_count=len(sources), selected_count=len(selected)
        )
        diagnostics["char_truncated_source_numbers"] = char_truncated_source_numbers
        if char_truncated_source_numbers and not diagnostics["truncated"]:
            diagnostics["truncation_reason"] = "raw_source_char_budget"
        diagnostics["truncated"] = (
            diagnostics["truncated"] or bool(char_truncated_source_numbers)
        )
        return selected, diagnostics

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


def _no_truncation_diagnostics() -> dict[str, object]:
    return {
        "total_count": 0,
        "selected_count": 0,
        "omitted_count": 0,
        "truncated": False,
        "truncation_reason": None,
        "char_truncated_source_numbers": [],
    }


def _source_count_diagnostics(
    *, total_count: int, selected_count: int
) -> dict[str, object]:
    omitted_count = total_count - selected_count
    return {
        "total_count": total_count,
        "selected_count": selected_count,
        "omitted_count": omitted_count,
        "truncated": omitted_count > 0,
        "truncation_reason": "raw_source_budget" if omitted_count > 0 else None,
    }
