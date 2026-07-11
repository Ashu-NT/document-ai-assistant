from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.appendix.raw_source_budget import (
    RawSourceBudget,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_context_bundle import (
    PromptContextBundle,
)


class PromptBudgetAllocator:
    def allocate(self, context: PromptContextBundle | None) -> RawSourceBudget:
        if context is None:
            return RawSourceBudget(max_sources=0, max_chars_per_source=0)
        if self._is_sparse(context):
            return RawSourceBudget(max_sources=4, max_chars_per_source=1200)
        if self._is_table_heavy(context):
            return RawSourceBudget(max_sources=2, max_chars_per_source=350)
        if self._is_maintenance_heavy(context):
            return RawSourceBudget(max_sources=3, max_chars_per_source=500)
        if self._is_rich(context):
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
