from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.appendix.raw_source_budget import (
    RawSourceBudget,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_context_bundle import (
    PromptContextBundle,
)

_REFERENCE_NUM_CTX = 8192
_MAX_SCALE = 4.0


class PromptBudgetAllocator:
    def __init__(self, *, num_ctx: int | None = None) -> None:
        self._scale = _scale_factor(num_ctx)

    def allocate(self, context: PromptContextBundle | None) -> RawSourceBudget:
        return _scaled(self._base_budget(context), self._scale)

    @staticmethod
    def _base_budget(context: PromptContextBundle | None) -> RawSourceBudget:
        if context is None:
            return RawSourceBudget(max_sources=0, max_chars_per_source=0)
        if PromptBudgetAllocator._is_sparse(context):
            return RawSourceBudget(max_sources=4, max_chars_per_source=1200)
        if PromptBudgetAllocator._is_table_heavy(context):
            return RawSourceBudget(max_sources=2, max_chars_per_source=350)
        if PromptBudgetAllocator._is_maintenance_heavy(context):
            return RawSourceBudget(max_sources=3, max_chars_per_source=500)
        if PromptBudgetAllocator._is_rich(context):
            return RawSourceBudget(max_sources=2, max_chars_per_source=450)
        return RawSourceBudget(max_sources=3, max_chars_per_source=700)

    @staticmethod
    def _is_sparse(context: PromptContextBundle) -> bool:
        return (
            context.source_count <= 1
            and not context.tables
            and not context.entities
            and not context.maintenance_entries
            and len(context.key_values) <= 1
        )

    @staticmethod
    def _is_table_heavy(context: PromptContextBundle) -> bool:
        return bool(context.tables) and context.answer_intent_value in {
            "table_summary",
            "specification_summary",
            "certification_summary",
        }

    @staticmethod
    def _is_maintenance_heavy(context: PromptContextBundle) -> bool:
        return bool(context.maintenance_entries) and context.answer_intent_value in {
            "maintenance_summary",
            "procedure_steps",
        }

    @staticmethod
    def _is_rich(context: PromptContextBundle) -> bool:
        richness_score = 0
        richness_score += int(bool(context.tables))
        richness_score += int(bool(context.entities))
        richness_score += int(bool(context.relationship_edges))
        richness_score += int(len(context.key_values) >= 4)
        richness_score += int(len(context.maintenance_entries) >= 2)
        return richness_score >= 2


def _scale_factor(num_ctx: int | None) -> float:
    if num_ctx is None or num_ctx <= _REFERENCE_NUM_CTX:
        return 1.0
    return min(_MAX_SCALE, num_ctx / _REFERENCE_NUM_CTX)


def _scaled(budget: RawSourceBudget, scale: float) -> RawSourceBudget:
    if scale == 1.0:
        return budget
    return RawSourceBudget(
        max_sources=max(budget.max_sources, round(budget.max_sources * scale)),
        max_chars_per_source=max(
            budget.max_chars_per_source, round(budget.max_chars_per_source * scale)
        ),
    )
